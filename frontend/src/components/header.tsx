"use client"

import { useState } from "react"
import { Bell, Search, User, LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useRouter } from "next/navigation"
import { auth } from "@/utils/api"

interface HeaderProps {
  userInfo?: any;
}

export function Header({ userInfo }: HeaderProps) {
  const router = useRouter();
  const [notifications, setNotifications] = useState([
    { id: 1, message: "Dr. Jacob Jones approved your data access request", time: "5 min ago" },
    { id: 2, message: "New lab results available", time: "1 hour ago" },
    { id: 3, message: "Appointment reminder: Dr. Theresa Webb tomorrow", time: "1 day ago" },
  ])

  const clearNotifications = () => {
    setNotifications([])
  }

  const handleLogout = () => {
    auth.clearUserData();
    router.push("/");
  }

  return (
    <header className="border-b bg-white">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex-1 md:flex-initial">
          <div className="relative w-full md:w-[400px]">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
            <Input
              type="search"
              placeholder="Search..."
              className="w-full bg-gray-50 pl-8 focus-visible:ring-blue-500"
            />
          </div>
        </div>
        <div className="flex items-center gap-4">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                {notifications.length > 0 && (
                  <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-xs text-white">
                    {notifications.length}
                  </span>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel className="flex items-center justify-between">
                Notifications
                {notifications.length > 0 && (
                  <Button variant="ghost" size="sm" onClick={clearNotifications}>
                    Clear all
                  </Button>
                )}
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              {notifications.length > 0 ? (
                notifications.map((notification) => (
                  <DropdownMenuItem key={notification.id} className="flex flex-col items-start py-2">
                    <span>{notification.message}</span>
                    <span className="text-xs text-gray-500">{notification.time}</span>
                  </DropdownMenuItem>
                ))
              ) : (
                <div className="py-4 text-center text-sm text-gray-500">No new notifications</div>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="rounded-full">
                <User className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>
                {userInfo?.name || 'My Account'}
                {userInfo?.role && (
                  <span className="block text-xs text-gray-500">
                    {userInfo.role === 'patient' ? 'Patient' : 'Healthcare Provider'}
                  </span>
                )}
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Profile</DropdownMenuItem>
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuItem>Data Access Log</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                <LogOut className="mr-2 h-4 w-4" />
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}
