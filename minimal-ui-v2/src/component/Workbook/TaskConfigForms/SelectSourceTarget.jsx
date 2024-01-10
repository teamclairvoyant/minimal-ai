import { Flex, Radio, Space, Tabs, Typography } from "antd";
import propTypes from "prop-types";
import { useEffect } from "react";

FileType.propTypes = {
  setTaskConfig: propTypes.func,
  taskConfig: propTypes.object,
  setButtonDisabled: propTypes.func,
};

function FileType({ taskConfig, setTaskConfig, setButtonDisabled }) {
  const types = [
    {
      label: "PARQUET",
      value: "parquet",
    },
    {
      label: "CSV",
      value: "csv",
    },
    {
      label: "JSON",
      value: "json",
    },
  ];

  return (
    <Space direction="vertical">
      <Radio.Group
        onChange={(e) => {
          setTaskConfig({ ...taskConfig, type: e.target.value });
          setButtonDisabled(false);
        }}
        defaultValue={"parquet"}
      >
        <Space direction="vertical" size={"middle"}>
          {types.map((item) => (
            <Radio.Button value={item.value} key={item.value}>
              {item.label}
            </Radio.Button>
          ))}
        </Space>
      </Radio.Group>
    </Space>
  );
}

//----------------------------------------------------------------------------------------------//

DWHTypes.propTypes = {
  setTaskConfig: propTypes.func,
  taskConfig: propTypes.object,
  setButtonDisabled: propTypes.func,
};

function DWHTypes({ taskConfig, setTaskConfig, setButtonDisabled }) {
  const types = [
    {
      label: "MYSQL",
      value: "mysql",
    },
    {
      label: "BIGQUERY",
      value: "bigquery",
    },
    {
      label: "REDSHIFT",
      value: "redshift",
    },
    {
      label: "POSTGRESSQL",
      value: "postgressql",
    },
  ];

  return (
    <Space direction="vertical">
      <Radio.Group
        onChange={(e) => {
          setTaskConfig({ ...taskConfig, type: e.target.value });
          setButtonDisabled(false);
        }}
        defaultValue={"parquet"}
      >
        <Space direction="vertical" size={"middle"}>
          {types.map((item) => (
            <Radio.Button value={item.value} key={item.value}>
              {item.label}
            </Radio.Button>
          ))}
        </Space>
      </Radio.Group>
    </Space>
  );
}

//----------------------------------------------------------------------------------------------//

SelectSourceTarget.propTypes = {
  taskConfig: propTypes.object,
  setTaskConfig: propTypes.func,
  setButtonDisabled: propTypes.func,
};

function SelectSourceTarget({ taskConfig, setTaskConfig, setButtonDisabled }) {
  useEffect(() => {
    setTaskConfig({
      ...taskConfig,
      source_target_area: "local_file",
      type: "parquet",
    });
  }, []);

  const setSourceArea = (item) => {
    setTaskConfig({ ...taskConfig, source_target_area: item });
  };

  const area = [
    {
      key: "local_file",
      label: "Local File",
      children: (
        <FileType
          taskConfig={taskConfig}
          setTaskConfig={setTaskConfig}
          setButtonDisabled={setButtonDisabled}
        />
      ),
    },
    {
      key: "gcp_bucket",
      label: "GCP Bucket",
      children: (
        <FileType
          taskConfig={taskConfig}
          setTaskConfig={setTaskConfig}
          setButtonDisabled={setButtonDisabled}
        />
      ),
    },
    {
      key: "warehouse",
      label: "Warehouse",
      children: (
        <DWHTypes
          taskConfig={taskConfig}
          setTaskConfig={setTaskConfig}
          setButtonDisabled={setButtonDisabled}
        />
      ),
    },
  ];

  return (
    <Flex vertical={true}>
      <Space size={70} style={{ paddingLeft: 25 }}>
        <Typography.Text
          strong
          style={{
            color: "rgb(147 147 147)",
            fontSize: "25px",
            fontWeight: "normal",
            lineHeight: "48px",
            margin: 0,
          }}
        >
          Area
        </Typography.Text>
        <Typography.Text
          strong
          style={{
            color: "rgb(147 147 147)",
            fontSize: "25px",
            fontWeight: "normal",
            lineHeight: "48px",
            margin: 0,
          }}
        >
          Type
        </Typography.Text>
      </Space>
      <Tabs
        defaultActiveKey="local_file"
        tabPosition={"left"}
        style={{
          height: 220,
        }}
        items={area}
        onTabClick={(item) => setSourceArea(item)}
      />
    </Flex>
  );
}
export default SelectSourceTarget;
