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


class InboundViewHolder (view: View) : RecyclerView.ViewHolder(view) {
    val requesterText: TextView = view.findViewById(R.id.requester)
    val amountText: TextView = view.findViewById(R.id.requested_spaghetti)
    val acceptButton: Button = view.findViewById(R.id.accept_button)
    val denyButton: Button = view.findViewById(R.id.deny_button)
}

class InboundRequestsAdapter(
        private val ctx: Context,
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
        // TODO accept button
        // TODO cancel button
    }
}