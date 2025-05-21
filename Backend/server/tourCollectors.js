require('dotenv').config();

const axios = require('axios');
const fs = require('fs');
const pLimit = require('p-limit');

const API_KEY = process.env.GOOGLE_PLACES_API_KEY;
const GU_LIST = [
  "강남", "강동", "강북", "강서", "관악", "광진", "구로", "금천", "노원",
  "도봉", "동대문", "동작", "마포", "서대문", "서초", "성동", "성북",
  "송파", "양천", "영등포", "용산", "은평", "종로", "중구", "중랑"
];

// 관광명소 관련 카테고리 (types)
const ALLOWED_TYPES = [
  'tourist_attraction',
  'museum',
  'park',
  'art_gallery',
  'point_of_interest',
  'establishment',
  'church',
  'hindu_temple',
  'synagogue',
  'mosque',
  'zoo',
  'amusement_park',
  'aquarium',
  'stadium',
  'library',
  'casino',
  'city_hall',
  'campground',
  'natural_feature',
  'local_government_office',
  'cemetery',
  'shopping_mall',
  'spa',
  'gym',
  'lodging',
];

// 구별로 "서울 {구} 관광명소" 쿼리 생성
const queries = GU_LIST.map(gu => `서울 ${gu} 관광명소`);

// 장소 중 ALLOWED_TYPES에 포함된 타입만 필터링하는 함수
function filterByTypes(places, allowedTypes = []) {
  return places.filter(place => 
    place.types && place.types.some(type => allowedTypes.includes(type))
  );
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
      // next_page_token 활성화 대기 (약 2초)
      await new Promise(res => setTimeout(res, 2000));
    }
  } while (nextPageToken);

  // 관광명소 관련 타입 필터링
  return filterByTypes(results, ALLOWED_TYPES);
}

async function getPlaceDetails(placeId) {
  const fields = 'name,rating,formatted_address,user_ratings_total,price_level,reviews,photos,types';
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
      console.log(`▶ 관광명소 검색 중: ${query}`);
      const places = await searchPlacesWithPagination(query);
      allPlaces.push(...places);
    }

    // 중복 제거 (place_id 기준)
    const uniquePlaces = Array.from(new Map(allPlaces.map(p => [p.place_id, p])).values());
    console.log(`🔍 총 수집된 유니크 관광명소 수 (필터 후): ${uniquePlaces.length}`);

    const limit = require('p-limit').default(5); // ✅ 간결하게 한 줄로
    const finalResults = [];

    const detailPromises = uniquePlaces.map(place =>
      limit(async () => {
        try {
          const detail = await getPlaceDetails(place.place_id);
          // 혹시 상세 정보에도 types 확인해서 다시 한번 필터링 가능 (선택 사항)
          if (!detail.types || !detail.types.some(t => ALLOWED_TYPES.includes(t))) {
            return; // 필터 제외
          }
          finalResults.push({
            name: detail.name,
            address: detail.formatted_address,
            rating: detail.rating,
            review_count: detail.user_ratings_total,
            price_level: Number.isInteger(detail.price_level) ? detail.price_level : null,
            reviews: detail.reviews?.slice(0, 3).map(r => r.text) ?? [],
            types: detail.types,
            image: getPhotoUrl(detail.photos?.[0]?.photo_reference)
          });
          console.log(`✔ 처리됨: ${detail.name}`);
        } catch (err) {
          console.warn(`❌ 상세 정보 실패: ${place.name}`);
        }
      })
    );

    await Promise.all(detailPromises);

    console.log(`🎉 최종 관광명소 수: ${finalResults.length}`);
    fs.writeFileSync('tourist_spots_data.json', JSON.stringify(finalResults, null, 2), 'utf-8');
    console.log('📁 관광명소 JSON 저장 완료: tourist_spots_data.json');

  } catch (err) {
    console.error('🔥 전체 오류 발생:', err.message);
  }
})();
