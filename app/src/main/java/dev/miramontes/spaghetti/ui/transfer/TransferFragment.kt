package dev.miramontes.spaghetti.ui.transfer

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import com.android.volley.Response
import dev.miramontes.spaghetti.R
import dev.miramontes.spaghetti.library.ServerConnection
import dev.miramontes.spaghetti.library.getIdToken
import okhttp3.internal.threadName

class TransferFragment : Fragment() {
    private var idToken: String = "NO_TOKEN";

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val root = inflater.inflate(R.layout.fragment_transfer, container, false)
        val amountField = root.findViewById<EditText>(R.id.amountField)
        val toSpinner = root.findViewById<Spinner>(R.id.toSpinner)
        val fromSpinner = root.findViewById<Spinner>(R.id.fromSpinner)
        val submitButton = root.findViewById<Button>(R.id.submitButton)

        activity?.let{ activity ->
            getIdToken(activity)?.let { newToken ->
                idToken = newToken
            }
            val serverConnection = ServerConnection(activity, idToken)

            // Get list of users
            serverConnection.listUsers(
                Response.Listener { response ->
                    Log.e("Spaghetti", "Response: " + response.toString(4))

                    // Split user ids and user names into lists
                    val users = response.getJSONArray("users")
                    val userIds = mutableListOf<Long>()
                    val userNames = mutableListOf<String>()
                    for (i in 0 until users.length()) {
                        val user = users.getJSONArray(i)
                        userIds.add(user.getLong(0))
                        userNames.add(user.getString(1))
                    }

                    // Hook up spinners

                    val arrayAdapter = ArrayAdapter(
                        activity,
                        R.layout.activity_spinner_dark,
                        userNames
                    )
                    arrayAdapter.setDropDownViewResource(R.layout.activity_spinner_dark_item)
                    fromSpinner.adapter = arrayAdapter
                    toSpinner.adapter = arrayAdapter

                    // Hook up submit button
                    submitButton.setOnClickListener {
                        val amount = try {
                            amountField.text.toString().toDouble()
                        } catch (e: NumberFormatException) {
                            0.0
                        }

                        if (amount == 0.0) {
                            Toast.makeText(activity, R.string.invalid_transfer_amount, Toast.LENGTH_LONG).show()
                        }
                        else {
                            serverConnection.createTransfer(
                                userIds[fromSpinner.selectedItemPosition],
                                userIds[toSpinner.selectedItemPosition],
                                amount,
                                Response.Listener { response ->
                                    Log.e("Spaghetti", "Response: " + response.toString(4))
                                },
                                Response.ErrorListener {
                                    Log.e("Spaghetti", "Failed to Authenticate with the server")
                                    activity.finish()
                                }
                            )
                        }
                    }
                },
                Response.ErrorListener {
                    Log.e("Spaghetti","Failed to Authenticate with the server")
                    activity.finish()
                }
            )
        }

        return root
    }
}