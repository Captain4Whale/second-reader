"use client";

import * as React from "react";
import { GripVerticalIcon } from "lucide-react";
import * as ResizablePrimitive from "react-resizable-panels";

import { cn } from "./utils";

function ResizablePanelGroup({
  className,
  ...props
}: React.ComponentProps<typeof ResizablePrimitive.PanelGroup>) {
  return (
    <ResizablePrimitive.PanelGroup
      data-slot="resizable-panel-group"
      className={cn(
        "flex h-full w-full data-[panel-group-direction=vertical]:flex-col",
        className,
      )}
      {...props}
    />
  );
}

function ResizablePanel({
  ...props
}: React.ComponentProps<typeof ResizablePrimitive.Panel>) {
  return <ResizablePrimitive.Panel data-slot="resizable-panel" {...props} />;
}

function ResizableHandle({
  withHandle,
  className,
  ...props
}: React.ComponentProps<typeof ResizablePrimitive.PanelResizeHandle> & {
  withHandle?: boolean;
}) {
  return (
    <ResizablePrimitive.PanelResizeHandle
      data-slot="resizable-handle"
      className={cn(
        "group focus-visible:ring-ring relative flex w-2 shrink-0 items-center justify-center bg-[var(--warm-100)] focus-visible:ring-1 focus-visible:ring-offset-1 focus-visible:outline-hidden after:absolute after:inset-y-0 after:left-1/2 after:w-px after:-translate-x-1/2 after:bg-[var(--warm-300)]/65 after:transition-colors hover:after:bg-[var(--amber-accent)]/45 data-[resize-handle-state=drag]:after:bg-[var(--amber-accent)]/65 data-[panel-group-direction=vertical]:h-2 data-[panel-group-direction=vertical]:w-full data-[panel-group-direction=vertical]:after:inset-x-0 data-[panel-group-direction=vertical]:after:top-1/2 data-[panel-group-direction=vertical]:after:h-px data-[panel-group-direction=vertical]:after:w-auto data-[panel-group-direction=vertical]:after:-translate-y-1/2 data-[panel-group-direction=vertical]:after:translate-x-0 [&[data-panel-group-direction=vertical]>div]:rotate-90",
        className,
      )}
      {...props}
    >
      {withHandle && (
        <div className="pointer-events-none z-10 flex h-8 w-4 items-center justify-center rounded-full border border-[var(--warm-300)]/70 bg-[var(--warm-50)]/95 text-[var(--warm-500)] opacity-0 shadow-sm transition-opacity duration-150 group-hover:opacity-100 group-data-[resize-handle-state=drag]:opacity-100">
          <GripVerticalIcon className="size-2.5" />
        </div>
      )}
    </ResizablePrimitive.PanelResizeHandle>
  );
}

export { ResizablePanelGroup, ResizablePanel, ResizableHandle };
