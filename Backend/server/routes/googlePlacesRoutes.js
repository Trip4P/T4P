const express = require('express');
const router = express.Router();
const pool = require('../db'); // db.js 연결
const axios = require('axios');

const API_KEY = process.env.GOOGLE_PLACES_API_KEY;

const GU_LIST = [
  "강남", "강동", "강북", "강서", "관악", "광진", "구로", "금천", "노원",
  "도봉", "동대문", "동작", "마포", "서대문", "서초", "성동", "성북",
  "송파", "양천", "영등포", "용산", "은평", "종로", "중구", "중랑"
];

const queries = GU_LIST.map(gu => `서울 ${gu} 맛집`);

async function searchPlaces(query) {
  const url = `https://maps.googleapis.com/maps/api/place/textsearch/json?query=${encodeURIComponent(query)}&key=${API_KEY}&language=ko`;
  const response = await axios.get(url);
  return response.data.results;
}

async function savePlaceToDB(place) {
  const query = `
    INSERT INTO meals (name, location, rating, review_count, price_level, image_url)
    VALUES ($1, $2, $3, $4, $5, $6)
    ON CONFLICT (name, location) DO UPDATE SET
      rating = EXCLUDED.rating,
      review_count = EXCLUDED.review_count,
      price_level = EXCLUDED.price_level,
      image_url = EXCLUDED.image_url;
  `;

  const values = [
    place.name,
    place.formatted_address,
    place.rating || null,
    place.user_ratings_total || null,
    place.price_level ?? null,
    place.photos?.length > 0 ?
      `https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=${place.photos[0].photo_reference}&key=${API_KEY}`
      : null
  ];

  try {
    await pool.query(query, values);
    console.log(`✅ 저장 성공: ${place.name}`);
  } catch (err) {
    console.error(`❌ 저장 실패: ${place.name} - ${err.message}`);
  }
}

router.get('/fetch', async (req, res) => {
  try {
    let allPlaces = [];

    for (const query of queries) {
      const places = await searchPlaces(query);
      allPlaces.push(...places);
    }

    // 중복 제거 (name + formatted_address 기준)
    const uniquePlacesMap = new Map();
    allPlaces.forEach(place => {
      const key = `${place.name}-${place.formatted_address}`;
      if (!uniquePlacesMap.has(key)) uniquePlacesMap.set(key, place);
    });
    const uniquePlaces = [...uniquePlacesMap.values()];

    // DB 저장 (병렬처리 - 최대 5개 동시)
    const pLimit = require('p-limit');
    const limit = pLimit(5);
    const savePromises = uniquePlaces.map(place => limit(() => savePlaceToDB(place)));
    await Promise.all(savePromises);

    res.json({ message: '구글 Places 데이터 수집 및 DB 저장 완료', count: uniquePlaces.length });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: '데이터 수집 중 오류 발생' });
  }
});

module.exports = router;
