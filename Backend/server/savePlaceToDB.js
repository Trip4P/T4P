const pool = require('./db');
const savePlaceReviewsToDB = require('./savePlaceReviewsToDB');

async function savePlaceToDB(place) {
  const client = await pool.connect();

  try {
    const query = `
      INSERT INTO destinations (
        place_id, name, location, rating, review_count, price_level, image_url,
        style_activity, style_hotplace, style_nature, style_landmark,
        style_healing, style_culture, style_photo, style_shopping, style_exotic,
        opening_hours, phone_number, created_at, area, opening_periods
      )
      VALUES (
        $1, $2, $3, $4, $5, $6, $7,
        $8, $9, $10, $11,
        $12, $13, $14, $15, $16,
        $17, $18, $19, $20, $21
      )
      ON CONFLICT (place_id) DO NOTHING;
    `;

    const values = [
      place.place_id,
      place.name,
      place.location,
      place.rating,
      place.review_count,
      place.price_level,
      place.image_url,
      place.style_activity,
      place.style_hotplace,
      place.style_nature,
      place.style_landmark,
      place.style_healing,
      place.style_culture,
      place.style_photo,
      place.style_shopping,
      place.style_exotic,
      place.opening_hours,
      place.phone_number,
      place.created_at,
      place.area,
      place.opening_periods
    ];

    await client.query(query, values);
    console.log(`✅ 저장 성공: ${place.name}`);

    if (place.reviews) {
      await savePlaceReviewsToDB(place.place_id, place.reviews);
    }
  } catch (err) {
    console.error(`❌ 저장 실패: ${place.name} -`, err.message);
  } finally {
    client.release();
  }
}

module.exports = savePlaceToDB;
