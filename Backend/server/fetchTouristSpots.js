require('dotenv').config();

const axios = require('axios');
const pLimit = require('p-limit');
const savePlaceToDB = require('./savePlaceToDB');

const API_KEY = process.env.GOOGLE_PLACES_API_KEY;
const GU_LIST = [
  "강남", "강동", "강북", "강서", "관악", "광진", "구로", "금천", "노원",
  "도봉", "동대문", "동작", "마포", "서대문", "서초", "성동", "성북",
  "송파", "양천", "영등포", "용산", "은평", "종로", "중구", "중랑"
];

const queries = GU_LIST.map(gu => `서울 ${gu} 관광지`);

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
  const fields = 'name,rating,formatted_address,user_ratings_total,price_level,photos';
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

    const detailPromises = uniquePlaces.map(place =>
      limit(async () => {
        try {
          const detail = await getPlaceDetails(place.place_id);
          const price_level = Number.isInteger(detail.price_level) ? detail.price_level : null;

          const data = {
            name: detail.name,
            location: detail.formatted_address,
            rating: detail.rating ?? null,
            review_count: detail.user_ratings_total ?? null,
            price_level: price_level,
            image_url: getPhotoUrl(detail.photos?.[0]?.photo_reference)
          };

          await savePlaceToDB(data);
        } catch (err) {
          console.warn(`❌ 상세 정보 실패: ${place.name} - ${err.message}`);
        }
      })
    );

    await Promise.all(detailPromises);

    console.log(`🎉 모든 관광지 정보 저장 완료!`);
  } catch (err) {
    console.error('🔥 전체 오류 발생:', err.message);
  }
})();
