const axios = require('axios');

const getRecommendationFromAI = async (preference) => {
  const prompt = `당신은 여행 플래너입니다.
사용자 성향은 다음과 같습니다:

- 감정 상태: ${preference.emotion}
- 여행 스타일: ${preference.styles.join(', ')}
- 일정 선호도: ${preference.schedule_preference}
- 동행자: ${preference.companions}

이 성향에 맞는 대한민국 여행 일정을 추천해 주세요.
1. 총 3일 일정을 표 형식으로 제공
2. 추천하는 관광지, 맛집, 카페 포함
3. 각 일정의 활동을 간단히 설명
4. 교통비, 식비, 입장료 등을 포함한 예산 요약을 아래에 표 형식으로 제시`;

  const response = await axios.post('https://api.openai.com/v1/chat/completions', {
    model: "gpt-4",
    messages: [{ role: "user", content: prompt }],
  }, {
    headers: {
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    }
  });

  return response.data.choices[0].message.content;
};

module.exports = { getRecommendationFromAI };