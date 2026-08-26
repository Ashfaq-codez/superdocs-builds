import { describe, it, expect, beforeEach, vi } from 'vitest';
import { JSDOM } from 'jsdom';
import fs from 'fs';
import path from 'path';

const html = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');

describe('HR Composer Frontend', () => {
  beforeEach(() => {
    const dom = new JSDOM(html);
    global.document = dom.window.document;
    global.window = dom.window;
    global.Office = { onReady: (cb) => cb() };
    vi.resetModules();
  });

  it('blocks submission if required fields are missing', async () => {
    const { getFormData } = await import('../src/ui.js');
    const data = getFormData();
    expect(data.candidate_name).toBe('');
    
    const { setError, state } = await import('../src/state.js');
    setError("All fields are required.");
    expect(state.error).toBe("All fields are required.");
  });

  it('updates state and UI correctly on successful composition', async () => {
    const { updateState, state } = await import('../src/state.js');
    const { render } = await import('../src/ui.js');
    
    updateState({
        composition_id: "123",
        status: "REVIEW_REQUIRED",
        jurisdiction_applied: "UK"
    });
    render();
    
    expect(state.data.status).toBe("REVIEW_REQUIRED");
    expect(document.getElementById('form-view').classList.contains('hidden')).toBe(true);
    expect(document.getElementById('status-view').classList.contains('hidden')).toBe(false);
    expect(document.getElementById('review-controls').classList.contains('hidden')).toBe(false);
    expect(document.getElementById('export-controls').classList.contains('hidden')).toBe(true);
  });

  it('hides review controls and shows export controls on approval', async () => {
    const { updateState } = await import('../src/state.js');
    const { render } = await import('../src/ui.js');
    
    updateState({ composition_id: "123", status: "APPROVED" });
    render();
    
    expect(document.getElementById('review-controls').classList.contains('hidden')).toBe(true);
    expect(document.getElementById('export-controls').classList.contains('hidden')).toBe(false);
  });
  
  it('renders artifacts on export completion', async () => {
    const { updateState } = await import('../src/state.js');
    const { render } = await import('../src/ui.js');
    
    updateState({ 
        composition_id: "123", status: "EXPORTED",
        artifacts: [{ format: "PDF", reference: "mock://pdf" }]
    });
    render();
    
    expect(document.getElementById('artifacts-view').classList.contains('hidden')).toBe(false);
    expect(document.getElementById('artifacts-list').innerHTML).toContain('mock://pdf');
  });
  
  it('displays API errors in the error banner', async () => {
    const { setError } = await import('../src/state.js');
    const { render } = await import('../src/ui.js');
    
    setError("Missing required template field.");
    render();
    
    const banner = document.getElementById('error-banner');
    expect(banner.classList.contains('hidden')).toBe(false);
    expect(banner.textContent).toBe("Missing required template field.");
  });

  it('transforms unsupported location errors into user-friendly messages', async () => {
    const { setError, state } = await import('../src/state.js');
    const { render } = await import('../src/ui.js');
    
    // Simulate the exact HTTP 400 error string returned by the Phase 3 backend
    setError("Unsupported location: 'bengaluru'");
    
    // Spy on console.error to verify the debug logging requirement
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    render();
    
    const banner = document.getElementById('error-banner');
    expect(banner.classList.contains('hidden')).toBe(false);
    
    // Assert the UX message is correct
    expect(banner.textContent).toContain("Location not supported.");
    expect(banner.textContent).toContain("'bengaluru' is outside the jurisdictions");
    
    // Assert we do NOT advertise STANDARD
    expect(banner.textContent).not.toContain("Standard");
    
    // Assert the original error was logged for debugging
    expect(consoleSpy).toHaveBeenCalledWith("[HR Composer Debug] Backend Error:", "Unsupported location: 'bengaluru'");
    
    consoleSpy.mockRestore();
  });
});