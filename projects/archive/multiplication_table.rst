.. _project-multiply:

Multiplication Table
====================

This was a quick code question I was asked once upon a time. They said I
wouldn't be able to use bash because it's not capable and that formatting
doesn't matter. Of course, I took both of those statements as a challenge.

The default shows 1*1 through 9*9, but an extra argument can be passed to
change the upper limit.

.. code-block:: sh

   #!/bin/bash
   max="${1:-9}"

   # Print header (space, range{1..max})
   printf '  '
   for ((i=1; i<=$max; i++)); do
   	printf '%7s' "$i"
   done
   printf '\n'

   for ((row=1; row<=$max; row++)); do
   	# Print multiplier
   	printf "%-2s" "$row"
   	for ((col=1; col<=$max; col++)); do
   		# Print products
   		printf '%7s' "$(($row * $col))"
   	done
   	printf '\n'
   done
