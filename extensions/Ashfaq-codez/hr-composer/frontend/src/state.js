export const state = {
    data: null,
    error: null
};

export function updateState(newData) {
    state.data = newData;
    state.error = null;
}

export function setError(msg) {
    state.error = msg;
}

export function resetState() {
    state.data = null;
    state.error = null;
}