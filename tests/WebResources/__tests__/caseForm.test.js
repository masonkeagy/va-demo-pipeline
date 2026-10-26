import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import CaseForm from '../caseForm';

describe('CaseForm Component', () => {
  test('renders form with initial values', () => {
    render(<CaseForm />);
    expect(screen.getByLabelText(/Case Title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
  });

  test('allows user to input text and submit form', () => {
    const handleSubmit = jest.fn();
    render(<CaseForm onSubmit={handleSubmit} />);

    const titleInput = screen.getByLabelText(/Case Title/i);
    const descriptionInput = screen.getByLabelText(/Description/i);
    const submitButton = screen.getByRole('button', { name: /Submit/i });

    fireEvent.change(titleInput, { target: { value: 'Test Case' } });
    fireEvent.change(descriptionInput, { target: { value: 'Test Description' } });
    fireEvent.click(submitButton);

    expect(handleSubmit).toHaveBeenCalledWith({
      title: 'Test Case',
      description: 'Test Description'
    });
  });

  test('shows validation error when title is empty', () => {
    render(<CaseForm />);
    const submitButton = screen.getByRole('button', { name: /Submit/i });
    fireEvent.click(submitButton);
    expect(screen.getByText(/Title is required/i)).toBeInTheDocument();
  });
});