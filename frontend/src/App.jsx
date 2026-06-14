import { useEffect, useState } from "react";
import RevenueChart from "./components/RevenueChart";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

const emptyItem = { name: "", item_type: "part", price: "", notes: "" };
const emptyJob = { vehicle_number: "", customer_name: "", vehicle_model: "", complaint: "" };
const emptyService = { job_id: "", service_item_id: "", description: "", quantity: "1", labor_charge: "0" };

function App() {
  const [items, setItems] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [revenue, setRevenue] = useState({ daily: [], monthly: [], yearly: [], total_revenue: 0 });
  const [itemForm, setItemForm] = useState(emptyItem);
  const [jobForm, setJobForm] = useState(emptyJob);
  const [serviceForm, setServiceForm] = useState(emptyService);
  const [paymentJobId, setPaymentJobId] = useState("");
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  async function api(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(readError(data));
    }
    return data;
  }

  function readError(data) {
    if (Array.isArray(data?.errors)) return data.errors.join(", ");
    if (typeof data?.errors === "object") {
      return Object.entries(data.errors).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`).join(" | ");
    }
    return data?.message || "Something went wrong.";
  }

  async function loadData() {
    const [itemsData, jobsData, revenueData] = await Promise.all([
      api("/items/"),
      api("/jobs/"),
      api("/revenue/"),
    ]);
    setItems(itemsData.items || []);
    setJobs(jobsData.jobs || []);
    setRevenue(revenueData);
  }

  async function submitItem(event) {
    event.preventDefault();
    try {
      setBusy("item");
      await api("/items/", { method: "POST", body: JSON.stringify(itemForm) });
      setItemForm(emptyItem);
      setMessage("Item added.");
      await loadData();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy("");
    }
  }

  async function submitJob(event) {
    event.preventDefault();
    try {
      setBusy("job");
      await api("/jobs/", { method: "POST", body: JSON.stringify(jobForm) });
      setJobForm(emptyJob);
      setMessage("Job created.");
      await loadData();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy("");
    }
  }

  async function submitService(event) {
    event.preventDefault();
    try {
      setBusy("service");
      await api("/services/", { method: "POST", body: JSON.stringify(serviceForm) });
      setServiceForm(emptyService);
      setMessage("Service line added.");
      await loadData();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy("");
    }
  }

  async function submitPayment(event) {
    event.preventDefault();
    if (!paymentJobId) return;
    try {
      setBusy("payment");
      await api(`/jobs/${paymentJobId}/pay/`, { method: "POST", body: JSON.stringify({}) });
      setPaymentJobId("");
      setMessage("Payment marked.");
      await loadData();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy("");
    }
  }

  const openJobs = jobs.filter((job) => job.status === "open");
  const paidJobs = jobs.filter((job) => job.status === "paid");
  const payableJobs = openJobs.filter((job) => job.services.length > 0);

  function money(value) {
    return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value || 0);
  }

  return (
    <div className="page-shell">
      <header className="hero-band">
        <div>
          <p className="tag">Fyn Mobility</p>
          <h1>Fyn Mobility</h1>
          <p className="subtitle">Vehicle service board for parts, jobs, billing, and revenue.</p>
        </div>
        <div className="hero-stats">
          <div><span>Revenue</span><strong>{money(revenue.total_revenue)}</strong></div>
          <div><span>Open</span><strong>{openJobs.length}</strong></div>
          <div><span>Paid</span><strong>{paidJobs.length}</strong></div>
        </div>
      </header>

      {message ? <div className="toast">{message}</div> : null}

      <section className="quick-grid">
        <div className="mini-panel lemon"><span>Catalog</span><strong>{items.length}</strong></div>
        <div className="mini-panel coral"><span>Jobs</span><strong>{jobs.length}</strong></div>
        <div className="mini-panel aqua"><span>Pay Ready</span><strong>{payableJobs.length}</strong></div>
      </section>

      <main className="content-grid">
        <section className="forms-stack">
          <form className="candy-card" onSubmit={submitItem}>
            <h2>Add Item</h2>
            <input placeholder="Item name" value={itemForm.name} onChange={(e) => setItemForm({ ...itemForm, name: e.target.value })} required />
            <div className="split-two">
              <select value={itemForm.item_type} onChange={(e) => setItemForm({ ...itemForm, item_type: e.target.value })}>
                <option value="part">New Part</option>
                <option value="repair">Repair Service</option>
              </select>
              <input type="number" min="0" step="0.01" placeholder="Price" value={itemForm.price} onChange={(e) => setItemForm({ ...itemForm, price: e.target.value })} required />
            </div>
            <input placeholder="Notes" value={itemForm.notes} onChange={(e) => setItemForm({ ...itemForm, notes: e.target.value })} />
            <button disabled={busy === "item"}>{busy === "item" ? "Saving..." : "Save Item"}</button>
          </form>

          <form className="candy-card pink" onSubmit={submitJob}>
            <h2>Create Job</h2>
            <div className="split-two">
              <input placeholder="Vehicle number" value={jobForm.vehicle_number} onChange={(e) => setJobForm({ ...jobForm, vehicle_number: e.target.value })} required />
              <input placeholder="Customer" value={jobForm.customer_name} onChange={(e) => setJobForm({ ...jobForm, customer_name: e.target.value })} required />
            </div>
            <input placeholder="Vehicle model" value={jobForm.vehicle_model} onChange={(e) => setJobForm({ ...jobForm, vehicle_model: e.target.value })} required />
            <textarea placeholder="Complaint" value={jobForm.complaint} onChange={(e) => setJobForm({ ...jobForm, complaint: e.target.value })} required />
            <button disabled={busy === "job"}>{busy === "job" ? "Saving..." : "Save Job"}</button>
          </form>

          <form className="candy-card violet" onSubmit={submitService}>
            <h2>Add Service</h2>
            <select value={serviceForm.job_id} onChange={(e) => setServiceForm({ ...serviceForm, job_id: e.target.value })} required>
              <option value="">Select job</option>
              {jobs.map((job) => <option key={job.id} value={job.id}>{job.vehicle_number}</option>)}
            </select>
            <select value={serviceForm.service_item_id} onChange={(e) => setServiceForm({ ...serviceForm, service_item_id: e.target.value })} required>
              <option value="">Select item</option>
              {items.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
            <input placeholder="Description" value={serviceForm.description} onChange={(e) => setServiceForm({ ...serviceForm, description: e.target.value })} required />
            <div className="split-three">
              <input type="number" min="1" step="1" placeholder="Qty" value={serviceForm.quantity} onChange={(e) => setServiceForm({ ...serviceForm, quantity: e.target.value })} required />
              <input type="number" min="0" step="0.01" placeholder="Labor" value={serviceForm.labor_charge} onChange={(e) => setServiceForm({ ...serviceForm, labor_charge: e.target.value })} required />
            </div>
            <button disabled={busy === "service"}>{busy === "service" ? "Saving..." : "Save Service"}</button>
          </form>

          <form className="candy-card mint" onSubmit={submitPayment}>
            <h2>Mark Payment</h2>
            <select value={paymentJobId} onChange={(e) => setPaymentJobId(e.target.value)}>
              <option value="">Select payable job</option>
              {payableJobs.map((job) => <option key={job.id} value={job.id}>{job.vehicle_number} - {money(job.total_amount)}</option>)}
            </select>
            <button disabled={busy === "payment" || !paymentJobId}>{busy === "payment" ? "Saving..." : "Mark Paid"}</button>
          </form>
        </section>

        <section className="board-stack">
          <div className="jobs-board">
            <div className="section-head">
              <h2>Active Jobs</h2>
              <span>{jobs.length} total</span>
            </div>
            <div className="job-list">
              {jobs.length ? jobs.map((job) => (
                <article className="job-card" key={job.id}>
                  <div className="job-top">
                    <div>
                      <h3>{job.vehicle_number}</h3>
                      <p>{job.vehicle_model} Ã¢â‚¬Â¢ {job.customer_name}</p>
                    </div>
                    <span className={`pill ${job.status}`}>{job.status_label}</span>
                  </div>
                  <p className="complaint">{job.complaint}</p>
                  <div className="service-chips">
                    {job.services.length ? job.services.map((service) => (
                      <span key={service.id} className="chip">{service.service_item_name} x {service.quantity}</span>
                    )) : <span className="chip ghost">No services yet</span>}
                  </div>
                  <div className="job-total">{money(job.total_amount)}</div>
                </article>
              )) : <div className="empty-box">Add an item and create your first job.</div>}
            </div>
          </div>

          <div className="charts-wrap">
            <RevenueChart title="Daily" data={revenue.daily || []} color="#ff6b6b" />
            <RevenueChart title="Monthly" data={revenue.monthly || []} color="#ffd93d" />
            <RevenueChart title="Yearly" data={revenue.yearly || []} color="#6bcBef" />
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
