const pool = require('./db');

async function saveMealReviewsToDB(placeId, reviews) {
  if (!reviews || reviews.length === 0) return;

  const client = await pool.connect();

  try {
    for (const review of reviews) {
      const comment = review.text;

      if (!comment || comment.length <= 10) continue;

      const createdAt = new Date(review.time * 1000).toISOString();

      const query = `
        INSERT INTO reviews (meal_id, comment, created_at)
        VALUES (
          (SELECT id FROM meals WHERE place_id = $1),
          $2,
          $3
        )
        ON CONFLICT DO NOTHING;
      `;

      await client.query(query, [placeId, comment, createdAt]);
    }
    console.log(`✅ 리뷰 저장 완료: place_id=${placeId}, 리뷰수=${reviews.length}`);
  } catch (err) {
    console.error(`❌ 리뷰 저장 실패: place_id=${placeId} -`, err.message);
  } finally {
    client.release();
  }
}

module.exports = saveMealReviewsToDB;
