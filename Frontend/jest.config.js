export default {
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  transform: {
    '^.+\\.jsx?$': 'babel-jest',
  },
  moduleFileExtensions: ['js', 'jsx'],
  setupFilesAfterEnv: ['<rootDir>/src/tests/setupTests.js'],
  globals: {
    TextEncoder: TextEncoder,
    TextDecoder: TextDecoder,
  },
  testEnvironmentOptions: {
    customExportConditions: [''],
  },
  // reporters: [
  //   "default",
  //   ["jest-html-reporter", {
  //     pageTitle: "제스트 테스트 리포터",
  //     outputPath: "test-report.html"
  //   }]
  // ]
};