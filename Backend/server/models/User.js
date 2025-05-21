const pool = require('../db');

async function addUser(name, email) {
  const query = `INSERT INTO users (name, email, created_at) VALUES ($1, $2, NOW()) RETURNING *`;
  const values = [name, email];
  const res = await pool.query(query, values);
  return res.rows[0];
}

async function addPreference(user_id, style_food, style_nature, style_city) {
  const query = `
    INSERT INTO preferences (user_id, style_food, style_nature, style_city, created_at)
    VALUES ($1, $2, $3, $4, NOW()) RETURNING *`;
  const values = [user_id, style_food, style_nature, style_city];
  const res = await pool.query(query, values);
  return res.rows[0];
}

module.exports = {
  addUser,
  addPreference,
};
