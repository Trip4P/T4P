// import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Greeting from './Greeting';

test('renders greeting message', () => {
  render(<Greeting name="Alice" />);
  expect(screen.getByText(/Hello, Alice/i)).toBeInTheDocument();
})