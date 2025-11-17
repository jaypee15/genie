import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ChatInput from '../ChatInput'

describe('ChatInput', () => {
  it('auto-focuses when enabled', () => {
    render(<ChatInput onSend={() => {}} disabled={false} placeholder="Type..." />)
    const textarea = screen.getByPlaceholderText('Type...')
    expect(textarea).toHaveFocus()
  })

  it('sends on Enter without Shift and clears input', () => {
    const onSend = vi.fn()
    render(<ChatInput onSend={onSend} disabled={false} placeholder="Say" />)
    const textarea = screen.getByPlaceholderText('Say')
    fireEvent.change(textarea, { target: { value: 'Hello' } })
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false })
    expect(onSend).toHaveBeenCalledWith('Hello')
    expect((textarea as HTMLTextAreaElement).value).toBe('')
  })
})


