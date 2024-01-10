import { createHook, createStore } from "react-sweet-state";

const Store = createStore({
  initialState: {
    task: {},
  },
  actions: {
    setTask:
      (currTask) =>
      ({ setState }) => {
        setState({
          task: currTask,
        });
      },
  },
  name: "TaskStore",
});

export const taskStore = createHook(Store);
