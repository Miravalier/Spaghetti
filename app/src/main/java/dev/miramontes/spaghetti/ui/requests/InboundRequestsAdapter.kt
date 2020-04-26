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


class InboundViewHolder (view: View) : RecyclerView.ViewHolder(view) {
    val requesterText: TextView = view.findViewById(R.id.requester)
    val amountText: TextView = view.findViewById(R.id.requested_spaghetti)
    val acceptButton: Button = view.findViewById(R.id.accept_button)
    val denyButton: Button = view.findViewById(R.id.deny_button)
}

class InboundRequestsAdapter(
        private val ctx: Activity,
        private val serverConnection: ServerConnection,
        private val fromUsers: MutableLiveData<MutableList<String>>,
        private val amounts: MutableLiveData<MutableList<Double>>,
        private val requestIds: MutableLiveData<MutableList<Long>>
    ) : RecyclerView.Adapter<InboundViewHolder>() {

    override fun getItemCount(): Int {
        return fromUsers.value?.size ?: 0
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): InboundViewHolder {
        return InboundViewHolder(LayoutInflater.from(ctx).inflate(
            R.layout.activity_inbound_requests_list, parent, false
        ))
    }

    override fun onBindViewHolder(holder: InboundViewHolder, position: Int) {
        holder.requesterText.text = fromUsers.value?.get(position) ?: ""
        holder.amountText.text = String.format("%.2f", amounts.value?.get(position) ?: 0.0)
        requestIds.value?.let { requestIds ->
            val requestId = requestIds[position]
            // Bind accept button
            holder.acceptButton.setOnClickListener {
                serverConnection.acceptRequest(
                    requestId,
                    Response.Listener { response ->
                        if (response.opt("success") != null) {
                            Toast.makeText(
                                ctx,
                                R.string.request_accept_success,
                                Toast.LENGTH_LONG
                            ).show()
                        }
                        else {
                            Log.e("Spaghetti", response.toString(4))
                            Toast.makeText(
                                ctx,
                                R.string.request_accept_fail,
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
            // Bind deny button
            holder.denyButton.setOnClickListener {
                serverConnection.denyRequest(
                    requestId,
                    Response.Listener { response ->
                        if (response.opt("success") != null) {
                            Toast.makeText(
                                ctx,
                                R.string.request_deny_success,
                                Toast.LENGTH_LONG
                            ).show()
                        }
                        else {
                            Log.e("Spaghetti", response.toString(4))
                            Toast.makeText(
                                ctx,
                                R.string.request_deny_fail,
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
}