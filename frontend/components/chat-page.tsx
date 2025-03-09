"use client"

import { useState } from "react"
import { ArrowDownAZ, ArrowUpAZ, Send, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

interface Message {
  id: string
  sender: {
    name: string
    avatar: string
    role: "doctor" | "patient"
  }
  content: string
  timestamp: Date
}

export function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: {
        name: "Dr. Johnson",
        avatar: "/placeholder.svg?height=40&width=40",
        role: "doctor",
      },
      content:
        "Based on your symptoms and initial examination, I recommend scheduling a follow-up appointment next week.",
      timestamp: new Date("2024-03-08T10:00:00"),
    },
    {
      id: "2",
      sender: {
        name: "You",
        avatar: "/placeholder.svg?height=40&width=40",
        role: "patient",
      },
      content: "Thank you, Dr. Johnson. Should I continue with the current medication until then?",
      timestamp: new Date("2024-03-08T10:05:00"),
    },
    {
      id: "3",
      sender: {
        name: "Dr. Johnson",
        avatar: "/placeholder.svg?height=40&width=40",
        role: "doctor",
      },
      content:
        "Yes, please continue with the prescribed dosage. If you experience any side effects, message me immediately.",
      timestamp: new Date("2024-03-08T10:07:00"),
    },
    {
      id: "4",
      sender: {
        name: "Dr. Smith",
        avatar: "/placeholder.svg?height=40&width=40",
        role: "doctor",
      },
      content:
        "Hello! I've reviewed your latest lab results. Everything looks good, but I'd like to discuss a few details.",
      timestamp: new Date("2024-03-07T14:30:00"),
    },
    {
      id: "5",
      sender: {
        name: "You",
        avatar: "/placeholder.svg?height=40&width=40",
        role: "patient",
      },
      content: "Of course, Dr. Smith. When would be a good time to discuss?",
      timestamp: new Date("2024-03-07T14:35:00"),
    },
    {
      id: "6",
      sender: {
        name: "Dr. Wilson",
        avatar: "/placeholder.svg?height=40&width=40",
        role: "doctor",
      },
      content: "Your prescription has been renewed and sent to your preferred pharmacy.",
      timestamp: new Date("2024-03-06T09:15:00"),
    },
  ])

  const [newMessage, setNewMessage] = useState("")
  const [sortAscending, setSortAscending] = useState(true)

  const handleSend = () => {
    if (newMessage.trim()) {
      const message: Message = {
        id: Date.now().toString(),
        sender: {
          name: "You",
          avatar: "/placeholder.svg?height=40&width=40",
          role: "patient",
        },
        content: newMessage.trim(),
        timestamp: new Date(),
      }
      setMessages([...messages, message])
      setNewMessage("")
    }
  }

  const handleDelete = (id: string) => {
    setMessages(messages.filter((message) => message.id !== id))
  }

  const toggleSort = () => {
    setSortAscending(!sortAscending)
    setMessages([...messages].reverse())
  }

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat("en-US", {
      hour: "numeric",
      minute: "numeric",
      month: "short",
      day: "numeric",
    }).format(date)
  }

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <div className="flex items-center justify-between border-b bg-white p-4">
        <h1 className="text-xl font-semibold">Messages</h1>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="icon">
              {sortAscending ? <ArrowDownAZ className="h-4 w-4" /> : <ArrowUpAZ className="h-4 w-4" />}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={toggleSort}>
              {sortAscending ? "Sort Newest First" : "Sort Oldest First"}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start gap-3 ${message.sender.role === "patient" ? "flex-row-reverse" : ""}`}
          >
            <img
              src={message.sender.avatar || "/placeholder.svg"}
              alt={message.sender.name}
              className="h-10 w-10 rounded-full"
            />
            <div className={`flex max-w-[70%] flex-col ${message.sender.role === "patient" ? "items-end" : ""}`}>
              <div className="mb-1 flex items-center gap-2">
                <span className="text-sm font-medium">{message.sender.name}</span>
                <span className="text-xs text-gray-500">{formatDate(message.timestamp)}</span>
              </div>
              <div
                className={`group relative rounded-lg p-3 ${
                  message.sender.role === "patient" ? "bg-blue-600 text-white" : "border bg-white"
                }`}
              >
                {message.content}
                <Button
                  variant="ghost"
                  size="icon"
                  className={`absolute -left-8 top-1/2 -translate-y-1/2 opacity-0 transition-opacity group-hover:opacity-100 ${
                    message.sender.role === "patient" ? "-right-8 left-auto" : ""
                  }`}
                  onClick={() => handleDelete(message.id)}
                >
                  <Trash2 className="h-4 w-4 text-red-500" />
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="border-t bg-white p-4">
        <div className="flex gap-2">
          <Input
            placeholder="Type a message..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
          />
          <Button onClick={handleSend}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
