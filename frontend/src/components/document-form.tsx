import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

const formSchema = z.object({
  bill_of_lading_number: z.string().nullable(),
  container_number: z.string().nullable(),
  consignee_name: z.string().nullable(),
  consignee_address: z.string().nullable(),
  date: z.string().nullable(),
  line_items_count: z.number().nullable(),
  average_gross_weight: z.number().nullable(),
  average_price: z.number().nullable(),
})

export function DocumentForm({ data, shouldHighlightField }: { 
  data: z.infer<typeof formSchema>
  shouldHighlightField?: (fieldName: keyof z.infer<typeof formSchema>) => boolean
}) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: data,
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log("Updated values:", values)
    // Here you would typically send the updated data to your backend
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
            control={form.control}
            name="bill_of_lading_number"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Bill of Lading Number</FormLabel>
                <FormControl>
                    <Input 
                      placeholder="BOL..." 
                      {...field} 
                      value={field.value ?? ""} 
                      className={cn(
                        shouldHighlightField?.("bill_of_lading_number") && "ring-2 ring-blue-500 bg-blue-50"
                      )}
                    />
                </FormControl>
                <FormMessage />
                </FormItem>
            )}
            />
            <FormField
            control={form.control}
            name="container_number"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Container Number</FormLabel>
                <FormControl>
                    <Input 
                      placeholder="Container..." 
                      {...field} 
                      value={field.value ?? ""} 
                      className={cn(
                        shouldHighlightField?.("container_number") && "ring-2 ring-blue-500 bg-blue-50"
                      )}
                    />
                </FormControl>
                <FormMessage />
                </FormItem>
            )}
            />
            <FormField
            control={form.control}
            name="consignee_name"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Consignee Name</FormLabel>
                <FormControl>
                    <Input 
                      placeholder="Consignee Name" 
                      {...field} 
                      value={field.value ?? ""} 
                      className={cn(
                        shouldHighlightField?.("consignee_name") && "ring-2 ring-blue-500 bg-blue-50"
                      )}
                    />
                </FormControl>
                <FormMessage />
                </FormItem>
            )}
            />
            <FormField
            control={form.control}
            name="consignee_address"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Consignee Address</FormLabel>
                <FormControl>
                    <Input 
                      placeholder="Consignee Address" 
                      {...field} 
                      value={field.value ?? ""} 
                      className={cn(
                        shouldHighlightField?.("consignee_address") && "ring-2 ring-blue-500 bg-blue-50"
                      )}
                    />
                </FormControl>
                <FormMessage />
                </FormItem>
            )}
            />
            <FormField
            control={form.control}
            name="date"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Date</FormLabel>
                <FormControl>
                    <Input 
                      placeholder="YYYY-MM-DD" 
                      {...field} 
                      value={field.value ?? ""} 
                      className={cn(
                        shouldHighlightField?.("date") && "ring-2 ring-blue-500 bg-blue-50"
                      )}
                    />
                </FormControl>
                <FormMessage />
                </FormItem>
            )}
            />
            <FormField
            control={form.control}
            name="line_items_count"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Line Items Count</FormLabel>
                <FormControl>
                    <Input 
                      type="number" 
                      {...field} 
                      value={field.value ?? ""} 
                      onChange={event => field.onChange(+event.target.value)} 
                      className={cn(
                        shouldHighlightField?.("line_items_count") && "ring-2 ring-blue-500 bg-blue-50"
                      )}
                    />
                </FormControl>
                <FormMessage />
                </FormItem>
            )}
            />
            <FormField
            control={form.control}
            name="average_gross_weight"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Average Gross Weight</FormLabel>
                <FormControl>
                    <Input 
                      type="number" 
                      {...field} 
                      value={field.value ?? ""} 
                      onChange={event => field.onChange(+event.target.value)} 
                      className={cn(
                        shouldHighlightField?.("average_gross_weight") && "ring-2 ring-blue-500 bg-blue-50"
                      )}
                    />
                </FormControl>
                <FormMessage />
                </FormItem>
            )}
            />
            <FormField
            control={form.control}
            name="average_price"
            render={({ field }) => (
                <FormItem>
                <FormLabel>Average Price</FormLabel>
                <FormControl>
                    <Input 
                      type="number" 
                      {...field} 
                      value={field.value ?? ""} 
                      onChange={event => field.onChange(+event.target.value)} 
                      className={cn(
                        shouldHighlightField?.("average_price") && "ring-2 ring-blue-500 bg-blue-50"
                      )}
                    />
                </FormControl>
                <FormMessage />
                </FormItem>
            )}
            />
        </div>
        <Button type="submit">Save Changes</Button>
      </form>
    </Form>
  )
}


