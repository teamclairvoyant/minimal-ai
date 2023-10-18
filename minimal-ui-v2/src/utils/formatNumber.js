import { replace } from "lodash";
import numeral from "numeral";

export function fShortenNumber(number) {
  return replace(numeral(number).format("0.00a"), ".00", "");
}
