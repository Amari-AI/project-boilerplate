"use client"

import * as React from "react"
import { CalendarIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

function formatDate(date: Date | undefined) {
  if (!date) {
    return ""
  }

  return date.toLocaleDateString("en-US", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  })
}

function isValidDate(date: Date | undefined) {
  if (!date) {
    return false
  }
  return !isNaN(date.getTime())
}

interface DatePickerProps {
  id?: string;
  label?: string;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  onBlur?: () => void;
}

export function DatePicker({ 
  id = "date", 
  label = "Date", 
  placeholder = "Select date...",
  value = "",
  onChange,
  onBlur
}: DatePickerProps) {
  const [open, setOpen] = React.useState(false)
  const [date, setDate] = React.useState<Date | undefined>(
    value ? new Date(value) : undefined
  )
  const [month, setMonth] = React.useState<Date | undefined>(date)
  const [displayValue, setDisplayValue] = React.useState(
    value ? formatDate(new Date(value)) : ""
  )

  // Update internal state when external value changes
  React.useEffect(() => {
    if (value) {
      const newDate = new Date(value);
      if (isValidDate(newDate)) {
        setDate(newDate);
        setMonth(newDate);
        setDisplayValue(formatDate(newDate));
      }
    } else {
      setDate(undefined);
      setDisplayValue("");
    }
  }, [value]);

  const handleInputChange = (inputValue: string) => {
    setDisplayValue(inputValue);
    
    const newDate = new Date(inputValue);
    if (isValidDate(newDate)) {
      setDate(newDate);
      setMonth(newDate);
      // Convert to YYYY-MM-DD format for form compatibility
      const isoDate = newDate.toISOString().split('T')[0];
      onChange?.(isoDate);
    } else {
      onChange?.(inputValue);
    }
  };

  const handleCalendarSelect = (selectedDate: Date | undefined) => {
    setDate(selectedDate);
    const formattedDisplay = formatDate(selectedDate);
    setDisplayValue(formattedDisplay);
    
    if (selectedDate) {
      // Convert to YYYY-MM-DD format for form compatibility
      const isoDate = selectedDate.toISOString().split('T')[0];
      onChange?.(isoDate);
    } else {
      onChange?.("");
    }
    
    setOpen(false);
  };

  return (
    <div className="flex flex-col gap-2">
      <Label htmlFor={id} className="text-sm font-medium">
        {label}
      </Label>
      <div className="relative flex gap-2">
        <Input
          id={id}
          value={displayValue}
          placeholder={placeholder}
          className="bg-background pr-10"
          onChange={(e) => handleInputChange(e.target.value)}
          onBlur={onBlur}
          onKeyDown={(e) => {
            if (e.key === "ArrowDown") {
              e.preventDefault()
              setOpen(true)
            }
          }}
        />
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button
              type="button"
              variant="ghost"
              className="absolute top-1/2 right-2 size-6 -translate-y-1/2"
            >
              <CalendarIcon className="size-3.5" />
              <span className="sr-only">Select date</span>
            </Button>
          </PopoverTrigger>
          <PopoverContent
            className="w-auto overflow-hidden p-0"
            align="end"
            alignOffset={-8}
            sideOffset={10}
          >
            <Calendar
              mode="single"
              selected={date}
              captionLayout="dropdown"
              month={month}
              onMonthChange={setMonth}
              onSelect={handleCalendarSelect}
            />
          </PopoverContent>
        </Popover>
      </div>
    </div>
  )
}