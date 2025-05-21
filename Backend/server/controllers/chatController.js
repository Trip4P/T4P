const { getRecommendationFromAI } = require('../services/chatService');

exports.recommend = async (req, res) => {
  try {
    const {
      emotion,
      styles,
      schedule_preference,
      companions
    } = req.body;

    const preference = {
      emotion,
      styles,
      schedule_preference,
      companions
    };

    const recommendation = await getRecommendationFromAI(preference);
    res.json({ recommendation });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
