const pool = require('../db');

async function addDestination(name, description, location, category, destination_type) {
  const query = `
    INSERT INTO destinations (name, description, location, category, destination_type)
    VALUES ($1, $2, $3, $4, $5) RETURNING *`;
  const values = [name, description, location, category, destination_type];
  const res = await pool.query(query, values);
  return res.rows[0];
}

async function addPlan(user_id, destination_id, start_date, end_date) {
  const query = `
    INSERT INTO plans (user_id, destination_id, start_date, end_date, created_at)
    VALUES ($1, $2, $3, $4, NOW()) RETURNING *`;
  const values = [user_id, destination_id, start_date, end_date];
  const res = await pool.query(query, values);
  return res.rows[0];
}

async function addDailyPlan(plan_id, day_number, date) {
  const query = `
    INSERT INTO daily_plan (plan_id, day_number, date)
    VALUES ($1, $2, $3) RETURNING *`;
  const values = [plan_id, day_number, date];
  const res = await pool.query(query, values);
  return res.rows[0];
}

async function addMeal(plans_id, destination_id, name, type, price) {
  const query = `
    INSERT INTO meals (plans_id, destination_id, name, type, price, created_at)
    VALUES ($1, $2, $3, $4, $5, NOW()) RETURNING *`;
  const values = [plans_id, destination_id, name, type, price];
  const res = await pool.query(query, values);
  return res.rows[0];
}

async function addReview(meal_id, rating, comment) {
  const query = `
    INSERT INTO reviews (meal_id, rating, comment, created_at)
    VALUES ($1, $2, $3, NOW()) RETURNING *`;
  const values = [meal_id, rating, comment];
  const res = await pool.query(query, values);
  return res.rows[0];
}

async function addBudget(plans_id, transport_cost, food_cost, entry_fees, total_budget) {
  const query = `
    INSERT INTO budget (plans_id, transport_cost, food_cost, entry_fees, total_budget, created_at)
    VALUES ($1, $2, $3, $4, $5, NOW()) RETURNING *`;
  const values = [plans_id, transport_cost, food_cost, entry_fees, total_budget];
  const res = await pool.query(query, values);
  return res.rows[0];
}

module.exports = {
  addDestination,
  addPlan,
  addDailyPlan,
  addMeal,
  addReview,
  addBudget,
};
