require('dotenv').config({ path: __dirname + '/.env' });
const axios = require('axios');
const fs = require('fs');
const pLimit = require('p-limit').default;
const saveMealToDB = require('./saveMealToDB');

const API_KEY = process.env.GOOGLE_PLACES_API_KEY;
const GU_LIST = [
"강남", "강동", "강북", "강서", "관악", "광진", "구로", "금천", "노원",
"도봉", "동대문", "동작", "마포", "서대문", "서초", "성동", "성북",
"송파", "양천", "영등포", "용산", "은평", "종로", "중구", "중랑"
];

// 10가지 스타일 배열
const STYLES = [
  '데이트용',
  '비즈니스 미팅',
  '기념일',
  '단체회식',
  '가족모임',
  '뷰 맛집',
  '상견례',
  '조용한 분위기',
  '모던한',
  '전통적인'
];

// 모든 구(GU)와 스타일 조합으로 쿼리 생성
const queries = [];
for (const gu of GU_LIST) {
  for (const style of STYLES) {
    queries.push({ query: `서울 ${gu} ${style} 맛집`, area: `서울 ${gu}구` });
  }
}


function analyzeStyles(place, detail) {
  const keywords = [
    place.name,
    detail.formatted_address,
    ...(detail.reviews?.map(r => r.text) || [])
  ].join(' ').toLowerCase();

  return {
    style_date: /데이트|감성|로맨틱/.test(keywords),
    style_business: /비즈니스|접대|코스요리|정식/.test(keywords),
    style_anniversary: /기념일|분위기 좋은|로맨틱/.test(keywords),
    style_team: /단체|회식|모임|넓은|룸/.test(keywords),
    style_family: /가족|어르신|아이와|가정식|한정식/.test(keywords),
    style_view: /뷰|전망|한강|야경|루프탑/.test(keywords),
    style_meeting: /상견례/.test(keywords),
    style_quiet: /조용|은은|아늑|한적/.test(keywords),
    style_modern: /모던|퓨전|깔끔|인테리어/.test(keywords),
    style_traditional: /전통|한정식|한옥|정갈/.test(keywords)
  };
}

async function searchPlacesWithPagination(query) {
  let results = [];
  let nextPageToken = null;
  let page = 1;

  do {
    const url = `https://maps.googleapis.com/maps/api/place/textsearch/json?query=${encodeURIComponent(query)}&key=${API_KEY}&language=ko${nextPageToken ? `&pagetoken=${nextPageToken}` : ''}`;
    const response = await axios.get(url);
    console.log(`📄 [${query}] Page ${page} 응답 상태:`, response.data.status);
    console.log(`🔢 [${query}] Page ${page} 결과 수:`, response.data.results?.length || 0);

    if (response.data.status !== 'OK' && response.data.status !== 'ZERO_RESULTS') {
      console.warn(`⚠️ API 오류 발생: ${response.data.status}`);
      break;
    }

    results = results.concat(response.data.results || []);
    nextPageToken = response.data.next_page_token;

    if (nextPageToken) {
      console.log(`⏳ 다음 페이지 토큰 있음 → 대기 중...`);
      await new Promise(res => setTimeout(res, 3000)); // 3초로 증가
      page++;
    }
  } while (nextPageToken);

  return results;
}

async function getPlaceDetails(placeId) {
  const fields = 'name,rating,formatted_address,user_ratings_total,price_level,reviews,photos,opening_hours,formatted_phone_number, geometry';
  const url = `https://maps.googleapis.com/maps/api/place/details/json?place_id=${placeId}&fields=${fields}&key=${API_KEY}&language=ko`;
  const response = await axios.get(url);

  if (!response.data || !response.data.result) {
    console.warn(`⚠️ Place detail 결과 없음: ${placeId}`);
  }

  return response.data.result;
}


function getPhotoUrl(photoReference) {
  if (!photoReference) return null;
  return `https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=${photoReference}&key=${API_KEY}`;
}
console.log(API_KEY);
(async () => {
  try {
    let allPlaces = [];

for (const { query, area } of queries) {
  console.log(`▶ 검색 중: ${query}`);
  const places = await searchPlacesWithPagination(query);
  allPlaces.push(...places.map(p => ({ ...p, area }))); // ✅ area 포함
}


    const uniquePlaces = Array.from(new Map(allPlaces.map(p => [p.place_id, p])).values());
    console.log(`🔍 총 수집된 유니크 장소 수: ${uniquePlaces.length}`);
    console.log("✅ 환경 변수 불러오기 테스트:", process.env.GOOGLE_PLACES_API_KEY);

    const limit = pLimit(5);
    const finalResults = [];


function classifyFoodType(text) {
  const lower = text.toLowerCase();

  const keywordGroups = [
    { type: '일식', keywords: ['스시', '초밥', '오마카세', '일식', '사시미', '돈카츠', '라멘', '우동'] },
    { type: '한식', keywords: ['비빔밥', '불고기', '된장', '한식', '한우', '한정식', '백반', '육회', '김치'] },
    { type: '중식', keywords: ['짜장면', '짬뽕', '탕수육', '중식', '마라', '딤섬', '중화요리'] },
    { type: '양식', keywords: ['스테이크', '파스타', '피자', '버거', '샐러드', '양식', '그릴'] },
    { type: '동남아식', keywords: ['쌀국수', '팟타이', '나시고렝', '태국', '베트남', '반미', '카오팟'] }
  ];

  for (const group of keywordGroups) {
    for (const keyword of group.keywords) {
      if (lower.includes(keyword)) return group.type;
    }
  }

  return '기타'; // 또는 null
}
    // 음식 종류 분류


    const detailPromises = uniquePlaces.map(place =>
      limit(async () => {
        try {
          const detail = await getPlaceDetails(place.place_id);

          if (typeof detail.price_level !== 'number' || detail.price_level < 1) {
            console.log(`🚫 저장 건너뜀 (price_level 없음 또는 1 미만): ${detail.name}`);
            return;
          }
          
          const imageUrl = getPhotoUrl(detail.photos?.[0]?.photo_reference);
if (!imageUrl) {
  console.log(`🚫 저장 건너뜀 (이미지 없음): ${detail.name}`);
  return;
}

          const combinedText = [
  place.name,
  detail.formatted_address,
  ...(detail.reviews?.map(r => r.text) || [])
].join(' ');

const food_type = classifyFoodType(combinedText); // 아까 만든 함수

          // 스타일 분류
          const styles = analyzeStyles(place, detail);

          const mealData = {
            place_id: place.place_id,
            name: detail.name,
            location: detail.formatted_address,
            latitude: detail.geometry?.location?.lat || null,
            longitude: detail.geometry?.location?.lng || null,
            rating: detail.rating,
            review_count: detail.user_ratings_total,
            price_level: detail.price_level,
            image_url: getPhotoUrl(detail.photos?.[0]?.photo_reference),
            ...styles,
            opening_hours: detail.opening_hours?.weekday_text?.join('\n') || null,
            phone_number: detail.formatted_phone_number || null,
            created_at: new Date().toISOString(),
            reviews: detail.reviews || [],
            food_type,
            area: place.area,
            opening_periods: detail.opening_hours?.periods ? JSON.stringify(detail.opening_hours.periods) : null,          
          };


          await saveMealToDB(mealData);
          finalResults.push(mealData);
          console.log(`✔ 처리 및 저장 완료: ${detail.name}`);
        } catch (err) {
          console.warn(`❌ 상세 정보 실패: ${place.name}`, err.message);
        }
      })
    );

    await Promise.all(detailPromises);
    console.log(`🎉 최종 저장된 장소 수: ${finalResults.length}`);

    fs.writeFileSync('places_data.json', JSON.stringify(finalResults, null, 2), 'utf-8');
    console.log('JSON 파일로 저장 완료: places_data.json');
  } catch (err) {
    console.error('🔥 전체 오류 발생:', err.message);
  }
})();
