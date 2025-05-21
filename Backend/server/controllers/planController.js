const Plan = require('../models/Plan');

exports.getPlans = async (req, res) => {
  try {
    const plans = await Plan.getPlans();
    res.json(plans);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};