import { createStore, createHook } from "react-sweet-state";

const Store = createStore({
  initialState: {
    pipeline: {},
  },
  actions: {
    setPipeline:
      (currPipeline) =>
      ({ setState }) => {
        setState({
          pipeline: currPipeline,
        });
      },
  },
  name: "PipelineStore",
});

export const pipelineStore = createHook(Store);
