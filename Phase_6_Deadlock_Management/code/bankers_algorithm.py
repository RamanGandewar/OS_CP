class BankersAlgorithm:
    def __init__(self, resources_state, allocation_rows):
        self.resource_order = [resource["resource_name"] for resource in resources_state]
        self.available = {resource["resource_name"]: resource["available_instances"] for resource in resources_state}
        self.allocation = {}
        self.maximum = {}

        for row in allocation_rows:
            process_id = row["process_id"]
            self.allocation.setdefault(process_id, {name: 0 for name in self.resource_order})
            self.maximum.setdefault(process_id, {name: 1 for name in self.resource_order})
            self.allocation[process_id][row["resource_name"]] = row["allocated_count"]
            self.maximum[process_id][row["resource_name"]] = row["allocated_count"] + max(row["requested_count"], 1)

    def is_safe_state(self):
        work = self.available.copy()
        finish = {process: False for process in self.maximum}
        safe_sequence = []

        changed = True
        while changed:
            changed = False
            for process, maximum in self.maximum.items():
                if finish[process]:
                    continue
                need = {resource: maximum[resource] - self.allocation[process][resource] for resource in self.resource_order}
                if all(need[resource] <= work[resource] for resource in self.resource_order):
                    for resource in self.resource_order:
                        work[resource] += self.allocation[process][resource]
                    finish[process] = True
                    safe_sequence.append(process)
                    changed = True

        return all(finish.values()), safe_sequence

    def request_resources(self, process_id, request):
        for resource, amount in request.items():
            if amount > self.available.get(resource, 0):
                return {"granted": False, "reason": "Request exceeds available resources", "safe_sequence": []}

        saved_available = self.available.copy()
        saved_allocation = {pid: alloc.copy() for pid, alloc in self.allocation.items()}
        self.allocation.setdefault(process_id, {name: 0 for name in self.resource_order})
        self.maximum.setdefault(process_id, {name: 1 for name in self.resource_order})

        for resource, amount in request.items():
            self.available[resource] -= amount
            self.allocation[process_id][resource] += amount
            self.maximum[process_id][resource] = max(self.maximum[process_id][resource], self.allocation[process_id][resource])

        safe, sequence = self.is_safe_state()
        if safe:
            return {"granted": True, "safe_sequence": sequence}

        self.available = saved_available
        self.allocation = saved_allocation
        return {"granted": False, "reason": "Unsafe state detected; Banker denied request", "safe_sequence": sequence}
