import React from "react";
import { Sidebar } from "../components/Sidebar";

export const Detail: React.FC = () => {
  return (
    <div className="layout">
      <Sidebar />

      <div className="content detail-page">
        {/* Success Banner */}
        <div className="detail-success">
          📄 Found 2 completed application(s)
        </div>

        {/* Filters */}
        <div className="detail-filters">
          <div className="filter-block">
            <label>🔍 Search by Name or ID</label>
            <input placeholder="Enter applicant name or unique ID..." />
          </div>

          <div className="filter-block">
            <label>Filter by Status</label>
            <select>
              <option>All</option>
              <option>Approved</option>
              <option>Declined</option>
            </select>
          </div>

          <div className="filter-block">
            <label>Sort by Date</label>
            <select>
              <option>Newest First</option>
              <option>Oldest First</option>
            </select>
          </div>
        </div>

        <div className="detail-count">Showing 2 application(s)</div>

        {/* Table */}
        <div className="table-wrapper">
          <table className="detail-table">
            <thead>
              <tr>
                <th>Unique ID</th>
                <th>Name</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Contact</th>
                <th>Final Premium</th>
                <th>Plan</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td>a94d7c08...</td>
                <td>Ramesh Kumar Verma</td>
                <td>63</td>
                <td>Male</td>
                <td>+91 9876543789</td>
                <td>₹0</td>
                <td>APPLICATION_DECLINED</td>
                <td className="status declined">
                  ❌ Application Declined
                </td>
              </tr>

              <tr>
                <td>983f466c...</td>
                <td>Amit Kumar Desai</td>
                <td>16</td>
                <td>Male</td>
                <td>+91 8765432101</td>
                <td>₹1,062</td>
                <td>GOLD_PLAN</td>
                <td className="status approved">
                  ✅ Approved
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Footer hint */}
        <div className="detail-footer">
          🔎 View Detailed Information
        </div>
      </div>
    </div>
  );
};