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
import Processing from "../../assets/procecssing.json";
import Success from "../../assets/success.json";
import "./parachain.css";

const BASE_URL: string = "https://127.0.0.1:3001/";

export default function ParaChain() {
  const [logs, setLogs] = useState<LogInterface[]>([]);
  const [connected, setConnected] = useState(false);
  const [mode, setMode] = useState("train");

  const [selectedModel, setSelectedModel] = useState(models[0]);
  const [selectedDataset, setSelectedDataset] = useState(datasets[0].label);
  const [trainingScores, setTrainingScores] = useState<{
    before: number;
    after: number;
  }>();

  const [evaluateScore, setEvaluateScore] = useState<number>();

  const [state, setState] = useState("initial");
  // states are initial, waiting, completed

  const updateLogs = () => {
    APIService.GetData(BASE_URL.concat("blocks")).then((data) => {
      setLogs(data.blocks);
    });
  };

  const updateConnectionStatus = () => {
    APIService.GetData(BASE_URL.concat("status"))
      .then(() => setConnected(true))
      .catch((err) => {
        console.log(err);
        setConnected(false);
      });
  };

  const initiateTraining = () => {
    setState("waiting");
    setMode("train");
    APIService.PostData(BASE_URL.concat("localupdate"), {
      dataset: datasets.find((d) => d.label === selectedDataset)?.value,
    }).then((scores) => {
      setState("completed");
      setTimeout(() => setState("initial"), 8000);
      setTrainingScores({
        before: fs(scores.before),
        after: fs(scores.after),
      });
      updateLogs();
    });
  };

  const initiateEvaluation = () => {
    // setState("waiting");
    setMode("evaluate");
    APIService.GetData(BASE_URL.concat("testmodel")).then((data) => {
      // console.log(data);
      // setState("completed");
      setEvaluateScore(fs(data.accuracy));
      updateLogs();
      // setTimeout(() => setState("initial"), 8000);
    });
  };

  const initiateSend = () => {
    APIService.PostData(BASE_URL.concat("send_data"), {});
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
            <Log mode="parachain" log={log} index={index} key={index} />
          ))}
        </div>
      </div>
      <div className="right">
        <div className="status noselect" onClick={updateConnectionStatus}>
          <div data-connected={connected ? "1" : "0"} className="icon" />
          {connected ? "Connected" : "Disconnected"}
        </div>
        <div className="animated-image">
          {state === "initial" && (
            <Lottie animationData={LearningRobot} loop={true} />
          )}
          {state === "waiting" && (
            <Lottie animationData={Processing} loop={true} />
          )}
          {state === "completed" && (
            <Lottie animationData={Success} loop={true} />
          )}
        </div>
        <h1>
          {state === "initial" && "Start Training"}
          {state === "waiting" && mode === "train" && "Training In-Progress"}
          {state === "waiting" &&
            mode === "evaluate" &&
            "Evaluation In-Progress"}
          {state === "completed" && "Training Completed"}
        </h1>
        <div className="row">
          <div className="col">
            <p>Available Models</p>
            <Dropdown
              options={models}
              selectedOption={selectedModel}
              setSelectedOption={() => {}}
              align="left"
            >
              <div className="selector">
                <p>{selectedModel}</p>
                <IoChevronDown />
              </div>
            </Dropdown>
          </div>
          <div className="col">
            <p>Select Dataset</p>
            <Dropdown
              options={datasets.map((i) => i.label)}
              selectedOption={selectedDataset}
              setSelectedOption={setSelectedDataset}
              align="left"
            >
              <div className="selector">
                <p>{selectedDataset}</p>
                <IoChevronDown />
              </div>
            </Dropdown>
          </div>
        </div>
        {trainingScores && mode === "train" && (
          <div className="row">
            <div className="col">
              <p>Accuracy Before</p>
              <span className="selector">{trainingScores.before}</span>
            </div>
            <div className="col">
              <p>Accuracy After</p>
              <span className="selector">{trainingScores.after}</span>
            </div>
          </div>
        )}
        {evaluateScore && mode === "evaluate" && (
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
            onClick={initiateTraining}
            disabled={state !== "initial"}
          >
            Initiate Training
          </button>
          <button
            className="mine-btn"
            onClick={initiateEvaluation}
            disabled={state !== "initial"}
          >
            Evaluate Model
          </button>
          <button
            className="training-btn"
            onClick={initiateSend}
            disabled={state !== "initial"}
          >
            Send to Relay Chain
          </button>
        </div>
      </div>
    </div>
  );
}
