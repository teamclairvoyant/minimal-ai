import { Button, Table } from "antd";
import propTypes from "prop-types";
import { useEffect, useState } from "react";
import { backendApi } from "../../../../../minimal-ui/src/api/api";
import { pipelineStore } from "../../../appState/pipelineStore";

const columns = [
  {
    title: "Column Name",
    dataIndex: "COLUMN_NAME",
  },
  {
    title: "Column Type",
    dataIndex: "COLUMN_TYPE",
  },
  {
    title: "Is Nullable",
    dataIndex: "IS_NULLABLE",
  },
];

SelectColumns.propTypes = {
  task: propTypes.object,
  setCloseForm: propTypes.func,
};

function SelectColumns({ task, setCloseForm }) {
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [{ pipeline }, { setPipeline }] = pipelineStore();
  const [data, setData] = useState([]);

  useEffect(() => {
    const get_data = async () => {
      try {
        const response = await backendApi.get(
          `/pipeline/${pipeline.uuid}/task/${task.id}/schema`
        );
        if (response.data) {
          setData(response.data);
        }
      } catch (error) {
        console.log(error.message);
        setData([]);
      }
    };
    get_data();
  }, [task]);

  const save = async () => {
    console.log(selectedRowKeys);
    const response = await backendApi.put(
      `/pipeline/${pipeline.uuid}/task/${task.id}/addColumn`,
      { columns: selectedRowKeys }
    );
    setPipeline(response.data.pipeline);
    setSelectedRowKeys([]);
    setCloseForm(false);
  };

  const onSelectChange = (newSelectedRowKeys) => {
    console.log("selectedRowKeys changed: ", newSelectedRowKeys);
    setSelectedRowKeys(newSelectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
  };

  const hasSelected = selectedRowKeys.length > 0;

  return (
    <div>
      <div
        style={{
          marginBottom: 16,
        }}
      >
        <Button type="primary" onClick={save} disabled={!hasSelected}>
          Save
        </Button>
      </div>
      <Table
        rowSelection={rowSelection}
        columns={columns}
        dataSource={data}
        rowKey={"COLUMN_NAME"}
      />
    </div>
  );
}

export default SelectColumns;
