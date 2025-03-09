"use client"

import { useState } from "react"
import { useRouter, usePathname } from "next/navigation"
import { Calendar, Home, MessageSquare, Settings, Users } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { NavigationItem } from "@/components/navigation-item"

interface NavigationSidebarProps {
  onLogout?: () => void
}

export function NavigationSidebar({ onLogout }: NavigationSidebarProps) {
  const [collapsed, setCollapsed] = useState(false)
  const router = useRouter()
  const pathname = usePathname()

  const toggleSidebar = () => {
    setCollapsed(!collapsed)
  }

  const navigateTo = (path: string) => {
    router.push(path)
  }

  return (
    <div className={cn("flex flex-col border-r bg-white transition-all duration-300", collapsed ? "w-16" : "w-64")}>
      <div className="flex h-16 items-center border-b px-4">
        <button
          onClick={toggleSidebar}
          className="flex items-center gap-2 focus:outline-none"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-blue-600 text-white">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          {!collapsed && <span className="font-semibold">MedChain</span>}
        </button>
      </div>

      <div className="flex-1 overflow-auto py-2">
        <nav className="grid gap-1 px-2">
          <NavigationItem
            icon={Home}
            label="Dashboard"
            active={pathname === "/dashboard"}
            collapsed={collapsed}
            onClick={() => navigateTo("/dashboard")}
          />
          <NavigationItem
            icon={Calendar}
            label="Appointments"
            active={pathname === "/appointments"}
            collapsed={collapsed}
            onClick={() => navigateTo("/appointments")}
          />
          <NavigationItem
            icon={MessageSquare}
            label="Chat"
            active={pathname === "/chat"}
            collapsed={collapsed}
            onClick={() => navigateTo("/chat")}
          />
          <NavigationItem
            icon={Users}
            label="Providers"
            active={pathname === "/providers"}
            collapsed={collapsed}
            onClick={() => navigateTo("/providers")}
          />
        </nav>
      </div>
      <div className="border-t p-2">
        <NavigationItem
          icon={Settings}
          label="Settings"
          active={pathname === "/settings"}
          collapsed={collapsed}
          onClick={() => navigateTo("/settings")}
        />
        <Button
          variant="outline"
          className={cn("mt-2 w-full", collapsed ? "justify-center px-0" : "justify-start")}
          onClick={onLogout || (() => router.push("/"))}
        >
          {collapsed ? "Exit" : "Log out"}
        </Button>
      </div>
    </div>
  )
}
