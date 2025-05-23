const pool = require('./db');
const saveMealReviewsToDB = require('./saveMealReviewsToDB'); //리뷰는 리뷰디비로

async function saveMealToDB(place) {
  const client = await pool.connect();
  try {
    const query = `
    INSERT INTO meals (
        name, location, rating, review_count, price_level, image_url,
        style_date, style_business, style_anniversary, style_team, style_family,
        style_view, style_meeting, style_quiet, style_modern, style_traditional,
        opening_hours, phone_number, place_id, created_at, food_type, area, opening_periods,
        latitude, longitude
    )
    VALUES ($1, $2, $3, $4, $5, $6,
            $7, $8, $9, $10, $11,
            $12, $13, $14, $15, $16,
            $17, $18, $19, $20, $21, $22, $23, $24, $25)
    ON CONFLICT (name, location) DO NOTHING;
`;

const values = [
  place.name,
  place.location,
  place.rating,
  place.review_count,
  place.price_level,
  place.image_url,
  place.style_date,
  place.style_business,
  place.style_anniversary,
  place.style_team,
  place.style_family,
  place.style_view,
  place.style_meeting,
  place.style_quiet,
  place.style_modern,
  place.style_traditional,
  place.opening_hours,
  place.phone_number,
  place.place_id,    
  place.created_at,
  place.food_type,
  place.area,
  place.opening_periods,
  place.latitude,
  place.longitude  
];


    await client.query(query, values);
    console.log(`✅ 저장 성공: ${place.name}`);
    if (place.reviews) {
      await saveMealReviewsToDB(place.place_id, place.reviews);
    }
  } catch (err) {
    console.error(`❌ 저장 실패: ${place.name} -`, err.message);
  } finally {
    client.release();
  }
}
module.exports = saveMealToDB;
