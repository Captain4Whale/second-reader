"use client";

import { createElement, useEffect, useMemo, useRef, useState, type CSSProperties, type HTMLAttributes } from "react";

import { Tooltip, TooltipContent, TooltipTrigger } from "./tooltip";
import { cn } from "./utils";

type OverflowTooltipTextProps = {
  as?: "div" | "h1" | "h2" | "h3" | "p" | "span";
  className?: string;
  "data-testid"?: string;
  lines?: number;
  side?: "top" | "right" | "bottom" | "left";
  style?: CSSProperties;
  text: string;
  tooltipClassName?: string;
} & Omit<HTMLAttributes<HTMLElement>, "children">;

export function OverflowTooltipText({
  as = "span",
  className,
  lines = 1,
  side = "top",
  style,
  text,
  tooltipClassName,
  ...props
}: OverflowTooltipTextProps) {
  const elementRef = useRef<HTMLElement | null>(null);
  const [isOverflowing, setIsOverflowing] = useState(false);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) {
      return;
    }

    const measure = () => {
      const next =
        element.scrollWidth > element.clientWidth + 1 ||
        element.scrollHeight > element.clientHeight + 1;
      setIsOverflowing(next);
    };

    measure();

    if (typeof ResizeObserver === "undefined") {
      window.addEventListener("resize", measure);
      return () => window.removeEventListener("resize", measure);
    }

    const observer = new ResizeObserver(measure);
    observer.observe(element);
    window.addEventListener("resize", measure);

    return () => {
      observer.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, [lines, text]);

  const sharedStyle = useMemo<CSSProperties>(() => {
    if (lines <= 1) {
      return {
        ...style,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap",
      };
    }

    return {
      ...style,
      display: "-webkit-box",
      overflow: "hidden",
      WebkitBoxOrient: "vertical",
      WebkitLineClamp: lines,
    };
  }, [lines, style]);

  const content = createElement(
    as,
    {
      ...props,
      ref: elementRef,
      className: cn(className, isOverflowing ? "cursor-help" : undefined),
      style: sharedStyle,
    },
    text,
  );

  if (!isOverflowing || !text.trim()) {
    return content;
  }

  return (
    <Tooltip>
      <TooltipTrigger asChild>{content}</TooltipTrigger>
      <TooltipContent
        side={side}
        sideOffset={8}
        className={cn(
          "max-w-[min(36rem,calc(100vw-2rem))] rounded-2xl border border-[var(--warm-300)]/65 bg-[var(--warm-50)] px-3.5 py-2 text-[var(--warm-900)] shadow-[0_18px_45px_rgba(61,46,31,0.14)]",
          tooltipClassName,
        )}
      >
        {text}
      </TooltipContent>
    </Tooltip>
  );
}
