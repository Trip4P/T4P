require('dotenv').config({ path: __dirname + '/.env' });
const axios = require('axios');
const fs = require('fs');
const pLimit = require('p-limit').default;
const savePlaceToDB = require('./savePlaceToDB');

const API_KEY = process.env.GOOGLE_PLACES_API_KEY;
const GU_LIST = [
"강남", "강동", "강북", "강서", "관악", "광진", "구로", "금천", "노원",
"도봉", "동대문", "동작", "마포", "서대문", "서초", "성동", "성북",
"송파", "양천", "영등포", "용산", "은평", "종로", "중구", "중랑"
];

const STYLES = [
  '체험', '액티비티', '핫플레이스', '자연', '랜드마크', '힐링',
  '문화', '사진', '쇼핑', '이국적인', '역사'
];

const ALLOWED_TYPES = [
  'tourist_attraction', 'museum', 'park', 'art_gallery', 'point_of_interest',
  'church', 'hindu_temple', 'synagogue', 'mosque', 'zoo',
  'amusement_park', 'aquarium', 'stadium', 'library', 'casino', 'city_hall',
  'campground', 'natural_feature', 'local_government_office', 'cemetery',
  'shopping_mall', 'spa', 'gym', 'lodging'
];

const EXCLUDE_TYPES = ['restaurant', 'food', 'meal_takeaway'];

function isAllowedPlace(types) {
  if (!types) return false;
  if (types.some(t => EXCLUDE_TYPES.includes(t))) return false;
  return types.some(t => ALLOWED_TYPES.includes(t));
}


// 키워드 기반 스타일 분석 함수
function analyzeStyles(detail) {
  const keywords = [
    detail.name,
    detail.formatted_address,
    ...(detail.reviews?.map(r => r.text) || [])
  ].join(' ').toLowerCase();

  return {
    style_activity: /체험|활동|액티비티|승마|패러글라이딩|카트|레저|공방|vr/.test(keywords),
    style_hotplace: /핫플|인스타|인기|줄서|인스타그램|sns|감성|핫한|유행/.test(keywords),
    style_nature: /산|숲|호수|계곡|자연|공원|해변|강|정원/.test(keywords),
    style_landmark: /유명|대표|랜드마크|필수|관광지|핫스팟/.test(keywords),
    style_healing: /힐링|조용|휴식|한적|편안|명상|산책/.test(keywords),
    style_culture: /문화|역사|예술|전시|박물관|미술관|유적|전통/.test(keywords),
    style_photo: /사진|포토|풍경|배경|뷰|인생샷|전망|야경|포인트/.test(keywords),
    style_shopping: /쇼핑|백화점|몰|아울렛|시장/.test(keywords),
    style_exotic: /이국|외국|유럽풍|일본풍|이탈리아|스페인|중세/.test(keywords)
  };
}

// 구글 플레이스 검색
async function searchPlacesWithPagination(query) {
  let results = [];
  let nextPageToken = null;

  do {
    const url = `https://maps.googleapis.com/maps/api/place/textsearch/json?query=${encodeURIComponent(query)}&key=${API_KEY}&language=ko${nextPageToken ? `&pagetoken=${nextPageToken}` : ''}`;
    const response = await axios.get(url);

    if (response.data.status !== 'OK' && response.data.status !== 'ZERO_RESULTS') {
      console.warn(`API 오류: ${response.data.status} for query "${query}"`);
      break;
    }

    results = results.concat(response.data.results);
    nextPageToken = response.data.next_page_token;

    if (nextPageToken) await new Promise(res => setTimeout(res, 2500)); // 토큰 대기
  } while (nextPageToken);

  return results.filter(place =>
    place.types && place.types.some(type => ALLOWED_TYPES.includes(type))
  );
}

// 장소 상세정보 조회
async function getPlaceDetails(placeId) {
  const fields = 'name,rating,formatted_address,user_ratings_total,price_level,reviews,photos,types,opening_hours,formatted_phone_number, geometry';
  const url = `https://maps.googleapis.com/maps/api/place/details/json?place_id=${placeId}&fields=${fields}&key=${API_KEY}&language=ko`;
  const response = await axios.get(url);

  if (response.data.status !== 'OK') {
    throw new Error(`Details API error: ${response.data.status}`);
  }

  return response.data.result;
}

// 사진 URL 생성
function getPhotoUrl(photoReference) {
  if (!photoReference) return null;
  return `https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=${photoReference}&key=${API_KEY}`;
}

(async () => {
  const limit = pLimit(5);

  try {
    const queries = [];
    for (const gu of GU_LIST) {
      for (const style of STYLES) {
        queries.push({ query: `서울 ${gu} ${style} 관광명소`, area: `서울 ${gu}구` });
      }
    }

    let allPlaces = [];

    for (const { query, area } of queries) {
      console.log(`▶ 관광명소 검색 중: ${query}`);
      const places = await searchPlacesWithPagination(query);
      allPlaces.push(...places.map(p => ({ ...p, area })));
    }

const seenAddrKeys = new Set();
const seenPlaceIds = new Set();
const uniquePlaces = [];

for (const place of allPlaces) {
  const idKey = place.place_id;
  const addrKey = `${place.name?.replace(/\s/g, '').toLowerCase()}-${place.formatted_address?.replace(/\s/g, '').toLowerCase()}`;

  if (!seenAddrKeys.has(addrKey) && !seenPlaceIds.has(idKey)) {
    seenAddrKeys.add(addrKey);
    seenPlaceIds.add(idKey);
    uniquePlaces.push(place);
  }
}

    console.log(`🔍 수집된 유니크 관광명소 수: ${uniquePlaces.length}`);

    const finalResults = [];

    const detailPromises = uniquePlaces.map(place =>
      limit(async () => {
        try {
          const detail = await getPlaceDetails(place.place_id);
          if (!detail.types || !detail.types.some(t => ALLOWED_TYPES.includes(t))) return;

          const styles = analyzeStyles(detail);

          const touristSpot = {
            place_id: place.place_id,
            area: place.area,
            name: detail.name,
            location: detail.formatted_address,
            latitude: detail.geometry?.location?.lat || null,
            longitude: detail.geometry?.location?.lng || null,
            rating: detail.rating || null,
            review_count: detail.user_ratings_total || 0,
            price_level: Number.isInteger(detail.price_level) ? detail.price_level : null,
            image_url: getPhotoUrl(detail.photos?.[0]?.photo_reference),
            opening_hours: detail.opening_hours?.weekday_text?.join('\n') || null,
            phone_number: detail.formatted_phone_number || null,
            ...styles,
            created_at: new Date().toISOString(),
            reviews: detail.reviews || [],
              opening_periods: detail.opening_hours?.periods ? JSON.stringify(detail.opening_hours.periods) : null,
          };
          if (!touristSpot.image_url) return;

          await savePlaceToDB(touristSpot);
          finalResults.push(touristSpot);
        } catch (err) {
          console.warn(`❌ 상세 정보 실패: ${place.name} - ${err.message}`);
        }
      })
    );

    await Promise.all(detailPromises);

    console.log(`🎉 최종 저장된 관광명소 수: ${finalResults.length}`);

    fs.writeFileSync('tourist_spots_data.json', JSON.stringify(finalResults, null, 2), 'utf-8');
    console.log('📁 관광명소 JSON 저장 완료: tourist_spots_data.json');

  } catch (err) {
    console.error(`🔥 전체 오류 발생: ${err.message}`);
  }
})();
