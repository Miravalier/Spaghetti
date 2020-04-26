package dev.miramontes.spaghetti.ui.requests


import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.lifecycle.MutableLiveData
import androidx.recyclerview.widget.RecyclerView
import dev.miramontes.spaghetti.R

class OutboundViewHolder (view: View) : RecyclerView.ViewHolder(view) {
    val requesterText: TextView = view.findViewById(R.id.requester)
    val amountText: TextView = view.findViewById(R.id.requested_spaghetti)
    val cancelButton: Button = view.findViewById(R.id.cancel_button)
}

class OutboundRequestsAdapter(
        private val ctx: Context,
        private val toUsers: MutableLiveData<MutableList<String>>,
        private val amounts: MutableLiveData<MutableList<Double>>,
        private val requestIds: MutableLiveData<MutableList<Long>>
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
        holder.amountText.text = String.format("%.2f", amounts.value?.get(position) ?: 0.0)
        // TODO cancel button
    }
}