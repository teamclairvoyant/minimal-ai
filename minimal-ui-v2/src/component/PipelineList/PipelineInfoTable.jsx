import { Flex, Table, Tag } from "antd";
import { filter } from "lodash";
import propTypes from "prop-types";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { backendApi } from "../../api/api";

const columns = [
  {
    title: "Pipeline UUID",
    dataIndex: "uuid",
    width: 100,
    fixed: "left",
    render: (text) => (
      <>
        <Link to={`/pipeline/${text}/edit`}>{text}</Link>
      </>
    ),
  },
  {
    title: "Pipeline Name",
    dataIndex: "name",
    width: 100,
    fixed: "left",
  },
  {
    title: "Schedule Status",
    dataIndex: "scheduleStatus",
    width: 100,
    fixed: "left",
  },
  {
    title: "Execution Status",
    dataIndex: "status",
    width: 100,
    fixed: "left",
  },
  {
    title: "Description",
    dataIndex: "description",
    width: 100,
  },
  {
    title: "Next Run Time",
    dataIndex: "nextRunTime",
    width: 100,
  },
  {
    title: "Created By",
    dataIndex: "createdBy",
    width: 100,
  },
  {
    title: "Created At",
    dataIndex: "createdAt",
    width: 100,
  },
  {
    title: "Modified By",
    dataIndex: "modifiedBy",
    width: 100,
  },
  {
    title: "Modified At",
    dataIndex: "modifiedat",
    width: 100,
  },
  {
    title: "Tasks",
    dataIndex: "tasks",
    width: 100,
  },
  {
    title: "Action",
    width: 100,
    fixed: "right",
    render: () => (
      <Flex gap={"small"}>
        <Tag bordered={false} color="orange">
          Logs
        </Tag>
        <Tag bordered={false} color="blue">
          Execute
        </Tag>
      </Flex>
    ),
  },
];

function getData(pipelines) {
  function dataArr(item) {
    return {
      uuid: item.uuid,
      name: item.name,
      scheduleStatus: item.scheduled ? "scheduled" : "not scheduled",
      status: item.status,
      description: item.description,
      nextRunTime: item.next_run_time,
      createdBy: item.created_by,
      createdAt: item.created_at,
      modifiedBy: item.modified_by,
      modifiedAt: item.modified_at,
      tasks: Object.keys(item.tasks).length,
    };
  }
  return pipelines.map(dataArr);
}

const PipelineInfoTable = ({ searchItem }) => {
  const [empty, setEmpty] = useState(false);
  const [pipelines, setPipelines] = useState([]);

  useEffect(() => {
    async function getSummary() {
      try {
        const response = await backendApi.get("/pipelines");
        if (response.data) {
          setPipelines(getData(response.data.pipelines));
        }
      } catch (error) {
        console.log(error.message);
      }
    }
    getSummary();
  }, []);

  if (!pipelines) setEmpty(true);

  function applyFilter(array, query) {
    if (query) {
      return filter(
        array,
        (_task) => _task.name.indexOf(query.toLowerCase()) !== -1
      );
    }
    return array;
  }

  const filterPipelines = applyFilter(pipelines, searchItem);

  return (
    <Table
      bordered={true}
      virtual
      columns={columns}
      scroll={{
        x: 2000,
        y: 450,
      }}
      rowKey="uuid"
      dataSource={empty ? [] : filterPipelines}
      pagination={false}
      style={{ marginTop: "1rem" }}
    />
  );
};

PipelineInfoTable.propTypes = {
  searchItem: propTypes.string,
};

export default PipelineInfoTable;
