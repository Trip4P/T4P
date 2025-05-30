describe('거기어때 테스트 시트', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173/TravelStyleForm');
  });



  it('지역과 카테고리를 선택하고 추천 결과를 확인한다.', () => {
    cy.wait(1000)

    cy.get('[data-testid="input-departure"]').type('서울역');
    cy.get('[data-testid="input-destination"]').type('부산역');
    cy.get('[data-testid="date-start"]').click(); // 날짜 선택 창 뜨는지 확인
    cy.get('.react-datepicker__day--015').click(); // 15일 선택
    cy.get('[data-testid="emotion-기쁜"]').click(); // 감정 선택
    cy.get('[data-testid="companion-친구와"]').click(); // 동행자 선택
    cy.get('[data-testid="input-people-count"]').clear().type('3');
    cy.get('[data-testid="btn-analyze"]').click(); // 분석 시작하기

  });
})