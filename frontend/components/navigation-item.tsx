"use client"

import type { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface NavigationItemProps {
  icon: LucideIcon
  label: string
  active?: boolean
  collapsed?: boolean
  onClick?: () => void
}

export function NavigationItem({ icon: Icon, label, active = false, collapsed = false, onClick }: NavigationItemProps) {
  const button = (
    <Button
      variant={active ? "default" : "ghost"}
      className={cn(
        "w-full",
        collapsed ? "justify-center px-0" : "justify-start",
        active ? "bg-blue-50 text-blue-700 hover:bg-blue-100 hover:text-blue-800" : "",
      )}
      onClick={onClick}
    >
      <Icon className="h-5 w-5 shrink-0" />
      {!collapsed && <span className="ml-2">{label}</span>}
    </Button>
  )

  if (collapsed) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>{button}</TooltipTrigger>
          <TooltipContent side="right">{label}</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    )
  }

  return button
}

