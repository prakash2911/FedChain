import { useState } from "react";
import { SiBlockchaindotcom } from "react-icons/si";

import { Log as LogInterface } from "../../models/logs";
import "./log.css";

interface LogProps {
  mode: "parachain" | "relaychain";
  log: LogInterface;
  index: number;
}

export default function Log({ mode, log, index }: LogProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div
      className="log-container noselect"
      key={index}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div className="header">
        <div className="left">
          <div className="logo">
            <SiBlockchaindotcom />
          </div>
          <div className="content">
            <h4>Block</h4>
            <p>Block Number {index + 1}</p>
          </div>
        </div>
        <p className="timestamp">{new Date(log.timestamp * 1000).toString()}</p>
      </div>
      <span>
        <h4>Current Hash</h4>
        <p>{log.hash}</p>
      </span>
      <span>
        <h4>Previous Hash</h4>
        <p>{log.previous_hash}</p>
      </span>
      {mode === "parachain" && isExpanded && (
        <>
          <span>
            <h4>From Address</h4>
            <p>{log.from_address}</p>
          </span>
          <span>
            <h4>To Address</h4>
            <p>{log.to_address}</p>
          </span>
          <span>
            <h4>Gas Used</h4>
            <p>{log.gas_used}</p>
          </span>
          <span>
            <h4>Type</h4>
            <p>{log.type}</p>
          </span>
        </>
      )}
    </div>
  );
}
