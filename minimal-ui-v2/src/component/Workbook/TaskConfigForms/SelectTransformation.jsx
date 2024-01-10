import { Flex, Input, Typography } from "antd";
import propTypes from "prop-types";

SelectTransformation.propTypes = {
  taskConfig: propTypes.object,
  setTaskConfig: propTypes.func,
  setButtonDisabled: propTypes.func,
};

const transformationType = [
  {
    label: "Join",
    value: "join",
  },
  {
    label: "Filter",
    value: "filter",
  },
  {
    label: "OrderBy",
    value: "orderby",
  },
  {
    label: "Limit",
    value: "limit",
  },
  {
    label: "Deduplicate",
    value: "deduplicate",
  },
  {
    label: "Aggregate",
    value: "aggregate",
  },
];

function SelectTransformation({
  taskConfig,
  setTaskConfig,
  setButtonDisabled,
}) {
  return (
    <Flex gap="middle" vertical>
      <Typography.Text
        style={{ fontSize: 20, padding: "1rem 0 1rem 1rem", color: "#bfbfbf" }}
      >
        Select Transformation Type
      </Typography.Text>
      <Flex gap="middle" style={{ padding: "0 1rem 0 1rem", flexWrap: "wrap" }}>
        {transformationType.map((i) => (
          <Input
            type="button"
            key={i.value}
            className="transform-card"
            onClick={(e) => {
              setTaskConfig({
                ...taskConfig,
                type: e.target.value.toLowerCase(),
              });
              setButtonDisabled(false);
            }}
            value={i.label}
          ></Input>
        ))}
      </Flex>
    </Flex>
  );
}

export default SelectTransformation;
