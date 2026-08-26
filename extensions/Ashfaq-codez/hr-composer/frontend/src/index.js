import { api } from './api.js';
import { state, updateState, setError, resetState } from './state.js';
import { render, getFormData } from './ui.js';

Office.onReady(() => {
    document.getElementById('btn-compose').onclick = async (e) => {
        e.preventDefault();
        const hrRecord = getFormData();
        if (!hrRecord.candidate_name || !hrRecord.role || !hrRecord.salary || !hrRecord.location || !hrRecord.start_date) {
            setError("All fields are required.");
            render();
            return;
        }
        
        document.getElementById('btn-compose').disabled = true;
        try {
            const res = await api.compose(hrRecord);
            updateState(res);
        } catch (err) {
            setError(err.message);
        } finally {
            document.getElementById('btn-compose').disabled = false;
            render();
        }
    };

    document.getElementById('btn-approve').onclick = async () => {
        try {
            const res = await api.approve(state.data.composition_id);
            updateState(res);
        } catch (err) { setError(err.message); }
        render();
    };

    document.getElementById('btn-reject').onclick = async () => {
        try {
            const res = await api.reject(state.data.composition_id);
            updateState(res);
        } catch (err) { setError(err.message); }
        render();
    };

    document.getElementById('btn-export').onclick = async () => {
        try {
            const res = await api.exportDoc(state.data.composition_id, ["PDF"]);
            updateState(res);
        } catch (err) { setError(err.message); }
        render();
    };

    document.getElementById('btn-reset').onclick = () => {
        resetState();
        render();
    };

    render();
});