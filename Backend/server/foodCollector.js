require('dotenv').config();
const axios = require('axios');
const fs = require('fs');
const pLimit = require('p-limit');
const saveMealToDB = require('./saveMealToDB');

const API_KEY = process.env.GOOGLE_PLACES_API_KEY;
const GU_LIST = [
  "강남"
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
    queries.push(`서울 ${gu} ${style} 맛집`);
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

  do {
    const url = `https://maps.googleapis.com/maps/api/place/textsearch/json?query=${encodeURIComponent(query)}&key=${API_KEY}&language=ko${nextPageToken ? `&pagetoken=${nextPageToken}` : ''}`;
    const response = await axios.get(url);
    results = results.concat(response.data.results);

    nextPageToken = response.data.next_page_token;
    if (nextPageToken) {
      await new Promise(res => setTimeout(res, 2000));
    }
  } while (nextPageToken);

  return results;
}

async function getPlaceDetails(placeId) {
  const fields = 'name,rating,formatted_address,user_ratings_total,price_level,reviews,photos,opening_hours,formatted_phone_number';
  const url = `https://maps.googleapis.com/maps/api/place/details/json?place_id=${placeId}&fields=${fields}&key=${API_KEY}&language=ko`;
  const response = await axios.get(url);
  return response.data.result;
}


function getPhotoUrl(photoReference) {
  if (!photoReference) return null;
  return `https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=${photoReference}&key=${API_KEY}`;
}

(async () => {
  try {
    let allPlaces = [];

    for (const query of queries) {
      console.log(`▶ 검색 중: ${query}`);
      const places = await searchPlacesWithPagination(query);
      allPlaces.push(...places);
    }

    const uniquePlaces = Array.from(new Map(allPlaces.map(p => [p.place_id, p])).values());
    console.log(`🔍 총 수집된 유니크 장소 수: ${uniquePlaces.length}`);

    const limit = pLimit(5);
    const finalResults = [];

    const detailPromises = uniquePlaces.map(place =>
      limit(async () => {
        try {
          const detail = await getPlaceDetails(place.place_id);

          if (typeof detail.price_level !== 'number' || detail.price_level < 1) {
            console.log(`🚫 저장 건너뜀 (price_level 없음 또는 1 미만): ${detail.name}`);
            return;
          }

          // 스타일 분류
          const styles = analyzeStyles(place, detail);

          const mealData = {
            place_id: place.place_id,
            name: detail.name,
            location: detail.formatted_address,
            rating: detail.rating,
            review_count: detail.user_ratings_total,
            price_level: detail.price_level,
            image_url: getPhotoUrl(detail.photos?.[0]?.photo_reference),
            ...styles,
            opening_hours: detail.opening_hours?.weekday_text?.join('\n') || null,
            phone_number: detail.formatted_phone_number || null,
            created_at: new Date().toISOString()
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
