const BASE_URL = "http://localhost:8000/compositions";

async function request(url, options = {}) {
    options.headers = { "Content-Type": "application/json", ...options.headers };
    const response = await fetch(url, options);
    if (!response.ok) {
        let errMessage = "Unknown Error";
        try {
            const errData = await response.json();
            errMessage = errData.detail || errMessage;
        } catch(e) {}
        throw new Error(errMessage);
    }
    return response.json();
}

export const api = {
    compose: (hrRecord) => request(BASE_URL, {
        method: "POST", body: JSON.stringify({ hr_record: hrRecord })
    }),
    approve: (id) => request(`${BASE_URL}/${id}/approve`, { method: "POST" }),
    reject: (id) => request(`${BASE_URL}/${id}/reject`, { method: "POST" }),
    exportDoc: (id, formats) => request(`${BASE_URL}/${id}/export`, { 
        method: "POST", body: JSON.stringify({ formats }) 
    })
};