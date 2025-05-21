const axios = require('axios');

const API_KEY = process.env.GOOGLE_PLACES_API_KEY;

// 다음 페이지까지 최대 50개 맛집을 받아오는 함수
async function getNearbyRestaurants(lat, lng, radius = 1500) {
  let allPlaces = [];
  let nextPageToken = null;

  do {
    let nearbyUrl = `https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=${lat},${lng}&radius=${radius}&type=restaurant&language=ko&key=${API_KEY}`;
    if (nextPageToken) {
      nearbyUrl += `&pagetoken=${nextPageToken}`;
      // 구글 API 정책상 다음 페이지 호출 전 약간 대기 필요 (2초)
      await new Promise((res) => setTimeout(res, 2000));
    }

    const nearbyResponse = await axios.get(nearbyUrl);
    console.log('Nearby API raw response:', nearbyResponse.data);

    allPlaces = allPlaces.concat(nearbyResponse.data.results);
    nextPageToken = nearbyResponse.data.next_page_token;

  } while (nextPageToken && allPlaces.length < 50);

  // 상세정보(평점, 리뷰, 주소 등) 받아오기
  const detailedPlaces = await Promise.all(
    allPlaces.map(async (place) => {
      const placeDetailsUrl = `https://maps.googleapis.com/maps/api/place/details/json?place_id=${place.place_id}&fields=name,rating,reviews,formatted_address&language=ko&key=${API_KEY}`;
      const detailsResponse = await axios.get(placeDetailsUrl);
      return {
        ...place,
        details: detailsResponse.data.result,
      };
    })
  );

  return detailedPlaces;
}

module.exports = { getNearbyRestaurants };
