import React, { useState } from "react";
import OutputSection from "./OutputSection";
import Monaco from "../Monaco/Monaco";
import LoadingAnimation from "../LoadingAnimation/LoadingAnimation";
import { runCode } from "../../utils/code";
import { ExecutionState } from "../../utils/ExecutionState";

const Child = ({ code }) => {
  const [runnableCode, setRunnableCode] = useState<string>(
    code.props.children.props.children
  );
  const [executionState, setExecutionState] = useState(ExecutionState.INIT);
  const [output, setOutput] = useState("");
  const [readonly, setReadonly] = useState(true);

  const execute = async () => {
    if (executionState === ExecutionState.STARTED) {
      return;
    }
    await clear();
    setExecutionState(ExecutionState.STARTED);
    setTimeout(async () => {
      await runCode(runnableCode, setOutput);
      setExecutionState(ExecutionState.ENDED);
    }, 10); // TODO: Remove workaround?
  };

  const clear = async () => {
    setOutput("");
    setExecutionState(ExecutionState.INIT);
  };
  const toggleReadonly = async () => {
    setReadonly(!readonly);
  };

  const numberOfLines = 1 + runnableCode.split("\n").length;
  const editorLayout = {
    width: 800,
    height: 18 * numberOfLines,
  };

  const setInput = (input: string) => {
    setRunnableCode(input);
  };

  return (
    <>
      {readonly ? (
        code
      ) : (
        <Monaco
          {...editorLayout}
          language="typescript"
          value={runnableCode}
          onChange={setInput}
          options={{
            scrollBeyondLastLine: false,
            minimap: { enabled: false },
            wordWrap: "on",
          }}
        />
      )}

      <OutputSection>
        <button
          className="button button--primary margin-right--xs"
          onClick={() => {
            execute();
          }}
        >
          Run Code
        </button>
        <button
          className="button button--secondary margin-right--xs"
          onClick={() => {
            toggleReadonly();
          }}
        >
          {readonly ? "Edit Code" : "Show Example"}
        </button>
        <button
          className="button button--secondary"
          onClick={() => {
            clear();
          }}
        >
          Clear Output
        </button>
        {executionState !== ExecutionState.INIT ? (
          <>
            <h4 className="margin-vert--md">Output</h4>
            <pre>
              <span className="d-align-items--center">
                {executionState === ExecutionState.STARTED ? (
                  <>
                    <LoadingAnimation />
                  </>
                ) : (
                  ""
                )}
                {output || executionState === ExecutionState.ENDED
                  ? output
                  : "Waiting for output..."}
              </span>
            </pre>
          </>
        ) : (
          ""
        )}
      </OutputSection>
    </>
  );
};

export const RunnableCode = (x) => {
  return <Child code={x.children}></Child>;
};
