import React from "react";

const MAP = {
  draft: "grey", validated: "teal", archived: "amber", deleted: "red",
  pending: "grey", running: "amber", completed: "teal", failed: "red",
};

export default function StatusBadge({ status }) {
  const cls = MAP[status] || "grey";
  return <span className={`badge badge-${cls}`}>{status}</span>;
}
