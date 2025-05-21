const pool = require('./db');

async function savePlaceToDB(place) {
  const client = await pool.connect();
  try {
    const query = `
      INSERT INTO meals (
        place_id, name, location, rating, review_count, price_level, image_url,
        style_date, style_business, style_anniversary, style_team, style_family,
        style_view, style_meeting, style_quiet, style_modern, style_traditional,
        opening_hours, phone_number, created_at
      )
      VALUES (
        $1, $2, $3, $4, $5, $6, $7,
        $8, $9, $10, $11, $12,
        $13, $14, $15, $16, $17,
        $18, $19, $20
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
      place.created_at
    ];

    await client.query(query, values);
    console.log(`✅ 저장 성공: ${place.name}`);
  } catch (err) {
    console.error(`❌ 저장 실패: ${place.name} -`, err.message);
  } finally {
    client.release();
  }
}

module.exports = savePlaceToDB;
