import { useState, useEffect } from "react";
import Lottie from "lottie-react";
import { IoReloadOutline, IoChevronDown } from "react-icons/io5";

import Dropdown from "../../components/Dropdown/Dropdown";
import Log from "../../components/Log/Log";
import APIService from "../../api/Service";

import { datasets, models } from "../../data";
import { Log as LogInterface } from "../../models/logs";
import { fs } from "../../utils";

import LearningRobot from "../../assets/learning-robot.json";
import "./relaychain.css";

const BASE_URL: string = "https://127.0.0.1:5000/";

export default function RelayChain() {
  const [logs, setLogs] = useState<LogInterface[]>([]);

  const [evaluateScore, setEvaluateScore] = useState<number>();

  const updateLogs = () => {
    APIService.GetData(BASE_URL.concat("blocks")).then((data) => {
      console.log(data);
      setLogs(data.blocks);
    });
  };

  const initiateEvaluation = () => {
    APIService.PostData(BASE_URL.concat("testModel"),{}).then((data) => {
      setEvaluateScore(fs(data.accuracy));
      updateLogs();
    });
  };

  useEffect(() => {
    updateLogs();
  }, []);

  return (
    <div className="page-container">
      <div className="left">
        <span className="toolbox">
          <div className="reload-button" onClick={updateLogs}>
            <IoReloadOutline />
          </div>
        </span>
        <div className="logs-wrapper">
          {logs.map((log: LogInterface, index: number) => (
            <Log mode="relaychain" log={log} index={index} key={index} />
          ))}
        </div>
      </div>
      <div className="right">
        <div className="animated-image">
          <Lottie animationData={LearningRobot} loop={true} />
        </div>
        <h1>Evaluate Model</h1>
        <div className="row">
          <div className="col">
            <p>Available Models</p>
            <Dropdown
              options={models}
              selectedOption={models[0]}
              setSelectedOption={() => {}}
              align="left"
            >
              <div className="selector">
                <p>{models[0]}</p>
                <IoChevronDown />
              </div>
            </Dropdown>
          </div>
          <div className="col">
            <p>Available Datasets</p>
            <Dropdown
              options={datasets.map((i) => i.label)}
              selectedOption={datasets[0].label}
              setSelectedOption={() => {}}
              align="left"
            >
              <div className="selector">
                <p>{datasets[0].label}</p>
                <IoChevronDown />
              </div>
            </Dropdown>
          </div>
        </div>
        {evaluateScore && (
          <div className="row">
            <div className="col">
              <p>Accuracy</p>
              <span className="selector">{evaluateScore}</span>
            </div>
          </div>
        )}
        <div className="btns-wrapper">
          <button
            className="training-btn"
            onClick={initiateEvaluation}
          >
            Evaluate Model
          </button>
        </div>
      </div>
    </div>
  );
}
