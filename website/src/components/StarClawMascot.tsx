/**
 * StarClaw mascot (same as logo symbol). Used in Hero and Nav.
 */
import { CatPawIcon } from "./CatPawIcon";

interface StarClawMascotProps {
  size?: number;
  className?: string;
}

export function StarClawMascot({ size = 80, className = "" }: StarClawMascotProps) {
  return <CatPawIcon size={size} className={className} />;
}
