import { state } from './state.js';

export function render() {
    const errorBanner = document.getElementById('error-banner');
    const formView = document.getElementById('form-view');
    const statusView = document.getElementById('status-view');
    
    if (state.error) {
        let displayError = state.error;
        
        // Intercept the specific backend UnsupportedJurisdictionError
        if (displayError.includes("Unsupported location")) {
            // Preserve the original backend error in the console for debugging
            console.error("[HR Composer Debug] Backend Error:", state.error);
            
            // Extract the location string if present
            const match = state.error.match(/Unsupported location: '(.*)'/);
            const locName = match ? match[1] : "The entered location";
            
            displayError = `Location not supported. '${locName}' is outside the jurisdictions currently supported by HR Composer. Supported locations include California (San Francisco, Los Angeles) and the UK (London, Manchester).`;
        }
        
        errorBanner.textContent = displayError;
        errorBanner.classList.remove('hidden');
    } else {
        errorBanner.classList.add('hidden');
    }

    if (!state.data) {
        formView.classList.remove('hidden');
        statusView.classList.add('hidden');
        return;
    }

    formView.classList.add('hidden');
    statusView.classList.remove('hidden');

    const d = state.data;
    const badge = document.getElementById('state-badge');
    badge.textContent = d.status.replace('_', ' ');
    badge.className = `status-badge status-${d.status}`;

    document.getElementById('lbl-id').textContent = d.composition_id || '-';
    document.getElementById('lbl-jur').textContent = d.jurisdiction_applied || '-';

    document.getElementById('review-controls').classList.toggle('hidden', d.status !== 'REVIEW_REQUIRED');
    document.getElementById('export-controls').classList.toggle('hidden', d.status !== 'APPROVED');
    
    const artifactsView = document.getElementById('artifacts-view');
    const artifactsList = document.getElementById('artifacts-list');
    if (d.status === 'EXPORTED' && d.artifacts) {
        artifactsView.classList.remove('hidden');
        artifactsList.innerHTML = d.artifacts.map(a => 
            `<li style="margin-bottom: 8px;">
               <div style="display:flex; flex-direction:column; gap:4px;">
                 <strong>${a.format} Document</strong> 
                 <span style="background-color: #f3f2f1; padding: 6px 8px; border-radius: 4px; font-family: monospace; font-size: 12px; color: #605e5c; border: 1px solid #e1dfdd; word-break: break-all;">
                   ${a.reference}
                 </span>
                 <em style="font-size: 11px; color: #a19f9d;">(Simulated Mock Environment Output)</em>
               </div>
             </li>`
        ).join('');
    } else {
        artifactsView.classList.add('hidden');
        artifactsList.innerHTML = '';
    }
}

export function getFormData() {
    return {
        candidate_name: document.getElementById('input-name').value.trim(),
        role: document.getElementById('input-role').value.trim(),
        salary: document.getElementById('input-salary').value.trim(),
        location: document.getElementById('input-location').value.trim(),
        start_date: document.getElementById('input-date').value.trim()
    };
}