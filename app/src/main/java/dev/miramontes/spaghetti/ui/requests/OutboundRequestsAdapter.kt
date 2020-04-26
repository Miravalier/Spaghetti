package dev.miramontes.spaghetti.ui.requests


import android.app.Activity
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.lifecycle.MutableLiveData
import androidx.recyclerview.widget.RecyclerView
import com.android.volley.Response
import dev.miramontes.spaghetti.R
import dev.miramontes.spaghetti.library.ServerConnection

class OutboundViewHolder (view: View) : RecyclerView.ViewHolder(view) {
    val requesterText: TextView = view.findViewById(R.id.requester)
    val amountText: TextView = view.findViewById(R.id.requested_spaghetti)
    val cancelButton: Button = view.findViewById(R.id.cancel_button)
}

class OutboundRequestsAdapter(
    private val ctx: Activity,
    private val serverConnection: ServerConnection,
    private val toUsers: MutableLiveData<MutableList<String>>,
    private val toAmounts: MutableLiveData<MutableList<Double>>,
    private val toRequestIds: MutableLiveData<MutableList<Long>>
    ) : RecyclerView.Adapter<OutboundViewHolder>() {

    override fun getItemCount(): Int {
        return toUsers.value?.size ?: 0
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): OutboundViewHolder {
        return OutboundViewHolder(LayoutInflater.from(ctx).inflate(
            R.layout.activity_outbound_requests_list, parent, false
        ))
    }

    override fun onBindViewHolder(holder: OutboundViewHolder, position: Int) {
        holder.requesterText.text = toUsers.value?.get(position) ?: ""
        holder.amountText.text = String.format("%.2f", toAmounts.value?.get(position) ?: 0.0)
        toRequestIds.value?.let { requestIds ->
            val requestId = requestIds[position]
            // Bind cancel button
            holder.cancelButton.setOnClickListener {
                serverConnection.denyRequest(
                    requestId,
                    Response.Listener { response ->
                        if (response.opt("success") != null) {
                            Toast.makeText(
                                ctx,
                                R.string.request_cancel_success,
                                Toast.LENGTH_LONG
                            ).show()
                            NetworkUpdate()
                        }
                        else {
                            Log.e("Spaghetti", response.toString(4))
                            Toast.makeText(
                                ctx,
                                R.string.request_cancel_fail,
                                Toast.LENGTH_LONG
                            ).show()
                        }
                    },
                    Response.ErrorListener {
                        Log.e("Spaghetti", "Failed to Authenticate with the server")
                        ctx.finish()
                    }
                )
            }
        }
    }

    fun NetworkUpdate() {
        // Make network requests to update watchable data
        serverConnection.listOutboundRequests(
            Response.Listener { response ->
                // Split reply into lists
                val requests = response.getJSONArray("requests")
                val users = mutableListOf<String>()
                val amounts = mutableListOf<Double>()
                val requestIds = mutableListOf<Long>()
                for (i in 0 until requests.length()) {
                    val request = requests.getJSONArray(i)
                    users.add(request.getString(0))
                    amounts.add(request.getDouble(2))
                    requestIds.add(request.getLong(3))
                }
                toUsers.value = users
                toAmounts.value = amounts
                toRequestIds.value = requestIds
                this.notifyDataSetChanged()
            },
            Response.ErrorListener {
                Log.e("Spaghetti","Failed to Authenticate with the server")
                ctx.finish()
            }
        )
    }
}